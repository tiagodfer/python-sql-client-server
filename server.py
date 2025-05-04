import sqlite3
import json
import queries
import socket
import multiprocessing
import re
import select
import urllib.parse
import ssl
import traceback

class Server():
    def __init__(self, host, port, cpf_db, cnpj_db, semaphore):
        super().__init__()
        self.host = host
        self.port = port
        self.cpf_db = cpf_db
        self.cnpj_db = cnpj_db
        self.server = None
        self.running = False
        self.semaphore = semaphore

    @staticmethod
    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
        except Exception:
            return '127.0.0.1'
        finally:
            s.close()

    @staticmethod
    def send_http_json(conn, data):
        try:
            # Convertendo para JSON com tamanho limitado de dados
            body = json.dumps(data, ensure_ascii=False)
            print(f"Enviando resposta com {len(body)} bytes")
            
            # Preparar o cabeçalho HTTP
            response = (
              "HTTP/1.1 200 OK\r\n"
              "Content-Type: application/json; charset=utf-8\r\n"
              "Access-Control-Allow-Origin: *\r\n"  # Permitir qualquer origem
              "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
              f"Content-Length: {len(body.encode('utf-8'))}\r\n"
              "\r\n"
              f"{body}"
            )
            
            # Converter para bytes
            response_bytes = response.encode('utf-8')
            
            # Enviar em pedaços de 8192 bytes para evitar problemas com pacotes muito grandes
            total_sent = 0
            while total_sent < len(response_bytes):
                chunk_size = min(8192, len(response_bytes) - total_sent)
                sent = conn.send(response_bytes[total_sent:total_sent + chunk_size])
                if sent == 0:
                    raise RuntimeError("Socket connection broken")
                total_sent += sent
                
            print(f"Resposta enviada com sucesso: {total_sent} bytes")
            
        except Exception as e:
            print(f"Erro ao enviar resposta: {e}")
            traceback.print_exc()

    @staticmethod
    def send_streaming_response(ssl_socket, query_func, params, cursor):
        try:
            # Enviar cabeçalhos iniciais
            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json; charset=utf-8\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
                "Transfer-Encoding: chunked\r\n"  # Importante para streaming
                "Connection: keep-alive\r\n"
                "\r\n"
            )
            ssl_socket.sendall(headers.encode('utf-8'))
            
            # Enviar status inicial
            initial_update = json.dumps({
                "status": "searching",
                "message": "Iniciando busca...",
                "progress": 0,
                "isComplete": False
            })
            chunk = f"{len(initial_update):X}\r\n{initial_update}\r\n"
            ssl_socket.sendall(chunk.encode('utf-8'))
            
            # Enviar atualização de 25%
            ssl_socket.sendall(
                f"{len(json.dumps({'status': 'searching', 'progress': 25, 'isComplete': False})):X}\r\n".encode('utf-8') +
                json.dumps({'status': 'searching', 'progress': 25, 'isComplete': False}).encode('utf-8') +
                "\r\n".encode('utf-8')
            )
            
            # Executar a consulta
            result = query_func(*params, cursor)
            
            # Enviar atualização de 75%
            ssl_socket.sendall(
                f"{len(json.dumps({'status': 'processing', 'progress': 75, 'isComplete': False})):X}\r\n".encode('utf-8') +
                json.dumps({'status': 'processing', 'progress': 75, 'isComplete': False}).encode('utf-8') +
                "\r\n".encode('utf-8')
            )
            
            # Preparar e enviar o resultado final
            final_result = json.dumps({
                "status": "complete", 
                "progress": 100, 
                "isComplete": True,
                "results": result
            })
            chunk = f"{len(final_result):X}\r\n{final_result}\r\n"
            ssl_socket.sendall(chunk.encode('utf-8'))
            
            # Terminar a resposta chunked
            ssl_socket.sendall("0\r\n\r\n".encode('utf-8'))
            
            print(f"Resposta streaming concluída com {len(result)} resultados")
            
        except Exception as e:
            print(f"Erro ao enviar resposta streaming: {e}")
            traceback.print_exc()
            
            # Tenta enviar mensagem de erro em caso de falha
            try:
                error_msg = json.dumps({"status": "error", "message": str(e), "isComplete": True})
                chunk = f"{len(error_msg):X}\r\n{error_msg}\r\n0\r\n\r\n"
                ssl_socket.sendall(chunk.encode('utf-8'))
            except:
                pass

    @staticmethod
    def handle_client(client_socket, addr, cpf_db, cnpj_db, semaphore):
        ssl_socket = None
        conn_cpf = None
        conn_cnpj = None
        
        try:
            # Wrap the socket with SSL
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
            
            # Set a timeout for the SSL handshake
            client_socket.settimeout(10.0)
            
            try:
                ssl_socket = context.wrap_socket(client_socket, server_side=True)
                print(f"SSL handshake successful with {addr}")
            except ssl.SSLError as e:
                print(f"SSL handshake failed with {addr}: {e}")
                return
            except Exception as e:
                print(f"Error during SSL wrap: {e}")
                return
            
            # Reset timeout after successful handshake
            ssl_socket.settimeout(30.0)
            
            # Open database connections
            conn_cpf = sqlite3.connect(cpf_db)
            conn_cnpj = sqlite3.connect(cnpj_db)
            cursor_cpf = conn_cpf.cursor()
            cursor_cnpj = conn_cnpj.cursor()

            # Receive data from client
            data = ssl_socket.recv(1024)
            if not data:
                print(f"No data received from {addr}")
                return
                
            request = data.decode()
            print(f"Request from {addr}: {request.splitlines()[0] if request else 'Empty'}")

            # Verificar se há cabeçalhos OPTIONS para pre-flight CORS
            if request.startswith("OPTIONS"):
                print("Recebida requisição OPTIONS (pre-flight CORS)")
                cors_response = (
                    "HTTP/1.1 204 No Content\r\n"
                    "Access-Control-Allow-Origin: *\r\n"
                    "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
                    "Access-Control-Allow-Headers: Content-Type\r\n"
                    "Access-Control-Max-Age: 86400\r\n"  # 24 horas
                    "\r\n"
                )
                ssl_socket.sendall(cors_response.encode('utf-8'))
                return

            # Nova rota: Health check
            if "GET /health" in request:
                print("Recebida solicitação de health check")
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n"
                    "Access-Control-Allow-Origin: *\r\n"  # Permitir qualquer origem
                    "Access-Control-Allow-Methods: GET, HEAD, OPTIONS\r\n"
                    "Connection: close\r\n"  # Importante para conexões HTTP/1.1
                    "Content-Length: 15\r\n"
                    "\r\n"
                    '{"status":"ok"}'
                )
                print("Enviando resposta health check:", response.replace('\r\n', '\\r\\n'))
                ssl_socket.sendall(response.encode('utf-8'))
                return

            # Adicionar cabeçalhos CORS a todas as respostas
            # /get-person-by-name/
            match = re.match(r"GET /get-person-by-name/([^ ]+) HTTP/1.[01]", request)
            if match:
                name = urllib.parse.unquote_plus(match.group(1))
                print(f"Buscando por nome: '{name}'")
                Server.send_streaming_response(ssl_socket, queries.search_cpf_by_name, (name,), cursor_cpf)
                return

            # Modificar todas as outras rotas da mesma forma, adicionando os cabeçalhos CORS
            # /get-person-by-exact-name/
            match = re.match(r"GET /get-person-by-exact-name/([^ ]+) HTTP/1.[01]", request)
            if match:
                name = urllib.parse.unquote_plus(match.group(1))
                print(f"Buscando por nome exato: '{name}'")
                Server.send_streaming_response(ssl_socket, queries.search_cpf_by_exact_name, (name,), cursor_cpf)
                return

            # /get-person-by-cpf/
            match = re.match(r"GET /get-person-by-cpf/(\d+) HTTP/1.[01]", request)
            if match:
                cpf = match.group(1)
                result = queries.search_cpf_by_cpf(cpf, cursor_cpf)
                Server.send_http_json(ssl_socket, {"results": result})
                return
                
            # /get-person-cnpj-by-name/
            match = re.match(r"GET /get-person-cnpj-by-name/([^ ]+) HTTP/1.[01]", request)
            if match:
                name = urllib.parse.unquote_plus(match.group(1))
                result = queries.check_person_cnpj(name, cursor_cnpj)
                Server.send_http_json(ssl_socket, {"results": result})
                return
                
            # /get-person-cnpj-by-name-cpf/
            match = re.match(r"GET /get-person-cnpj-by-name-cpf/([^-]+)-([^ ]+) HTTP/1.[01]", request)
            if match:
                name = urllib.parse.unquote_plus(match.group(1))
                cpf = urllib.parse.unquote_plus(match.group(2))
                # Execute query using the representante_legal and nome_representante columns
                cursor_cnpj.execute("SELECT * FROM socios WHERE representante_legal LIKE ? AND nome_representante LIKE ?", 
                                   ('%' + cpf[3:9] + '%', '%' + name + '%',))
                results = cursor_cnpj.fetchall()
                if results:
                    cpf_list = []
                    for row in results:
                        cpf_info = {
                            'nome fantasia': row[2],
                            'nome': row[8],
                            'cpf': row[7]
                        }
                        cpf_list.append(cpf_info)
                    Server.send_http_json(ssl_socket, {"results": cpf_list})
                else:
                    error_body = json.dumps({"error": "Não é sócio de nenhuma empresa"})
                    response = (
                        "HTTP/1.1 404 Not Found\r\n"
                        "Content-Type: application/json\r\n"
                        f"Content-Length: {len(error_body)}\r\n"
                        "\r\n"
                        f"{error_body}"
                    )
                    ssl_socket.sendall(response.encode("utf-8"))
                return

            # /get-person-cnpj-by-name-cpf-radical/
            match = re.match(r"GET /get-person-cnpj-by-name-cpf-radical/([^-]+)-([^ ]+) HTTP/1.[01]", request)
            if match:
                name = urllib.parse.unquote_plus(match.group(1))
                cpf = urllib.parse.unquote_plus(match.group(2))
                # Execute query using cpf_cnpj and nome columns
                cursor_cnpj.execute("SELECT * FROM socios WHERE cpf_cnpj LIKE ? AND nome LIKE ?", 
                                   ('%' + cpf[3:9] + '%', '%' + name + '%',))
                results = cursor_cnpj.fetchall()
                if results:
                    cpf_list = []
                    for row in results:
                        cpf_info = {
                            '0 - cpf': row[3],
                            '0 - nome': row[2],
                        }
                        cpf_list.append(cpf_info)
                        cursor_cnpj.execute("SELECT * FROM estabelecimentos WHERE radical = ?", (row[0],))
                        estab_results = cursor_cnpj.fetchall()
                        num_empresa = 0
                        if estab_results:
                            for estab_row in estab_results:
                                num_empresa += 1
                                key = f'{num_empresa} nome fantasia'
                                key2 = f'{num_empresa} rua'
                                key3 = f'{num_empresa} num'
                                key4 = f'{num_empresa} estado'
                                cpf_info[key] = estab_row[4]
                                cpf_info[key2] = estab_row[14]
                                cpf_info[key3] = estab_row[15]
                                cpf_info[key4] = estab_row[19]
                    Server.send_http_json(ssl_socket, {"results": cpf_list})
                else:
                    error_body = json.dumps({"error": "Não é sócio de nenhuma empresa"})
                    response = (
                        "HTTP/1.1 404 Not Found\r\n"
                        "Content-Type: application/json\r\n"
                        f"Content-Length: {len(error_body)}\r\n"
                        "\r\n"
                        f"{error_body}"
                    )
                    ssl_socket.sendall(response.encode("utf-8"))
                return

            # Invalid request
            error_body = json.dumps({"error": "Invalid request"})
            response = (
                "HTTP/1.1 400 Bad Request\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {len(error_body)}\r\n"
                "\r\n"
                f"{error_body}"
            )
            ssl_socket.sendall(response.encode("utf-8"))
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            traceback.print_exc()
        finally:
            if semaphore:
                semaphore.release()
            
            # Close database connections
            if conn_cpf:
                try:
                    conn_cpf.close()
                except:
                    pass
            if conn_cnpj:
                try:
                    conn_cnpj.close()
                except:
                    pass
            
            # Close sockets
            if ssl_socket:
                try:
                    ssl_socket.close()
                except:
                    pass
            
            try:
                client_socket.close()
            except:
                pass
            
            print(f"Connection with {addr} closed")

    def start(self):
        # Server configuration
        HOST = self.host
        PORT = self.port

        # Create socket
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen(5)
            
            self.server = server_socket
            
            local_ip = self.get_local_ip()
            print(f"[SERVER] Listening on {local_ip}:{PORT} (HTTPS)")

            # Start server
            self.running = True
            
            while self.running:
                try:
                    # Use select with a timeout to make the server interruptible
                    ready_to_read, _, _ = select.select([self.server], [], [], 1.0)
                    
                    if not ready_to_read:
                        continue
                        
                    # Accept connection
                    client_socket, addr = self.server.accept()
                    print(f"[CONNECTION] New connection from {addr}")
                    
                    # Acquire semaphore to limit simultaneous connections
                    self.semaphore.acquire()
                    
                    # Set a reasonable timeout
                    client_socket.settimeout(5.0)
                    
                    # Create a process to handle the client
                    # Pass the whole socket to the new process
                    process = multiprocessing.Process(
                        target=self.handle_client,
                        args=(client_socket, addr, self.cpf_db, self.cnpj_db, self.semaphore)
                    )
                    process.daemon = True
                    process.start()
                    
                    # Detach the socket from the parent process
                    # This prevents the parent from closing it
                    client_socket.detach()
                    
                except OSError as e:
                    if e.errno == 9:  # Bad file descriptor
                        print(f"Error accepting connection: socket may have been closed")
                    else:
                        print(f"Error accepting connection: {e}")
                        traceback.print_exc()
                except Exception as e:
                    print(f"Unexpected error in server loop: {e}")
                    traceback.print_exc()
                    
        except Exception as e:
            print(f"Error setting up server: {e}")
            traceback.print_exc()

    def stop(self):
        self.running = False
        if self.server:
            try:
                self.server.close()
            except:
                pass
            self.server = None

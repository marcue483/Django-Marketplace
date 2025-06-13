import win32file
import json
import time

class DockerPipeClient:
    def __init__(self, pipe_name=r'\\.\pipe\docker_engine'):
        self.pipe_name = pipe_name

    def _open_pipe(self):
        return win32file.CreateFile(
            self.pipe_name,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0, None,
            win32file.OPEN_EXISTING,
            0, None
        )

    def _send_request(self, method, path, data=None, headers=None):
        if headers is None:
            headers = {}
        headers.setdefault("Host", "localhost")
        headers.setdefault("Connection", "close")

        body = ""
        if data:
            if isinstance(data, dict):
                body = json.dumps(data)
                headers.setdefault("Content-Type", "application/json")
            else:
                body = str(data)
            headers["Content-Length"] = str(len(body))
        else:
            headers["Content-Length"] = "0"

        request_lines = [f"{method} {path} HTTP/1.1"]
        for k, v in headers.items():
            request_lines.append(f"{k}: {v}")
        request_lines.append("")
        request_lines.append(body)

        request_raw = "\r\n".join(request_lines).encode()

        handle = self._open_pipe()
        win32file.WriteFile(handle, request_raw)

        response = b""
        while True:
            try:
                part = win32file.ReadFile(handle, 4096)[1]
                if not part:
                    break
                response += part
            except Exception:
                break

        handle.close()

        try:
            header, body = response.split(b"\r\n\r\n", 1)
        except ValueError:
            print("Invalid HTTP response")
            return None

        if b"Transfer-Encoding: chunked" in header:
            full_body = b""
            while body:
                try:
                    length_str, body = body.split(b"\r\n", 1)
                    length = int(length_str.decode(), 16)
                    if length == 0:
                        break
                    chunk, body = body[:length], body[length+2:]
                    full_body += chunk
                except Exception:
                    break
            return full_body.decode()
        else:
            return body.decode(errors="ignore")

    def create_container(self, image="busybox", command=["sleep", "3600"]):
        data = {
            "Image": image,
            "Cmd": command,
            "Tty": False
        }
        resp = self._send_request("POST", "/containers/create", data=data)
        print("\n[CREATE RESPONSE]", resp)

        try:
            parsed = json.loads(resp)
            container_id = parsed["Id"]
            print(f"\n[+] Container created: {container_id}")
            return container_id
        except Exception as e:
            print(f"\n[!] Failed to parse container ID: {e}")
            return None

    def start_container(self, container_id):
        self._send_request("POST", f"/containers/{container_id}/start")
        print(f"[+] Started container {container_id}")

    def delete_container(self, container_id):
        self._send_request("DELETE", f"/containers/{container_id}?force=true")
        print(f"[+] Deleted container {container_id}")


if __name__ == "__main__":
    client = DockerPipeClient()

    container_id = client.create_container()
    if not container_id:
        print("\n[!] Aborting: container creation failed.")
        exit(1)

    time.sleep(1)
    client.start_container(container_id)
    time.sleep(1)

    input("\n[!] Container running. Press Enter to delete it...")
    time.sleep(1)

    client.delete_container(container_id)

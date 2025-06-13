import win32file
import json

class DockerNamedPipeClient:
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

        http_request = "\r\n".join(request_lines).encode()

        handle = self._open_pipe()
        win32file.WriteFile(handle, http_request)

        response = b""
        while True:
            try:
                chunk = win32file.ReadFile(handle, 4096)[1]
                if not chunk:
                    break
                response += chunk
            except Exception:
                break

        handle.close()

        response_text = response.decode(errors="ignore")
        parts = response_text.split("\r\n\r\n", 1)
        if len(parts) < 2:
            return None

        headers_text, body_text = parts
        return body_text


if __name__ == "__main__":
    client = DockerNamedPipeClient()

    containers_json = client._send_request("GET", "/containers/json")
    print("Containers JSON:", containers_json)makecontainer, flag delete aftermakecontainer, flag delete aftermakecontainer, flag delete aftermakecontainer, flag delete aftermakecontainer, flag delete after
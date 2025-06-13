import httpx
import json
import time
import sys

class DockerPipeClient:
    def __init__(self, base_url="http://localhost:2375"):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url)

    def create_container(self, image="busybox", command=["sh", "-c", "while true; do date; sleep 1; done"]):
        data = {
            "Image": image,
            "Cmd": command,
            "Tty": True,
            "AttachStdout": True,
            "AttachStderr": True
        }
        try:
            response = self.client.post("/containers/create", json=data)
            response.raise_for_status()
            parsed = response.json()
            container_id = parsed["Id"]
            print(f"\n[+] Container created: {container_id}")
            return container_id
        except httpx.HTTPError as e:
            print(f"\n[!] Failed to create container: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            print(f"\n[!] Failed to parse container ID: {e}")
            return None

    def start_container(self, container_id):
        try:
            response = self.client.post(f"/containers/{container_id}/start")
            response.raise_for_status()
            print(f"[+] Started container {container_id}")
        except httpx.HTTPError as e:
            print(f"\n[!] Failed to start container {container_id}: {e}")

    def stream_output(self, container_id):
        with self.client.stream('GET', f"/containers/{container_id}/logs?follow=true&stdout=true&stderr=true") as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    print(line)

    def delete_container(self, container_id):
        try:
            response = self.client.delete(f"/containers/{container_id}?force=true")
            response.raise_for_status()
            print(f"[+] Deleted container {container_id}")
        except httpx.HTTPError as e:
            print(f"\n[!] Failed to delete container {container_id}: {e}")

    def __del__(self):
        self.client.close()

if __name__ == "__main__":
    client = DockerPipeClient()

    container_id = client.create_container()
    if not container_id:
        print("\n[!] Aborting: container creation failed.")
        exit(1)

    time.sleep(1)
    client.start_container(container_id)
    time.sleep(1)

    print("\n[+] Streaming container output (Press Ctrl+C to stop)...")
    try:
        client.stream_output(container_id)
    except KeyboardInterrupt:
        print("\n[!] Stopping container...")
    except httpx.HTTPError as e:
        print(f"\n[!] Failed to stream container output: {e}")
    finally:
        print("[+] Cleaning up container...")
        client.delete_container(container_id)
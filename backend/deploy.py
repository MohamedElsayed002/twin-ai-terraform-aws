import os
import shutil
import subprocess
import zipfile


def docker_available() -> bool:
    try:
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_dependencies() -> None:
    print("Installing dependencies for Lambda runtime...")

    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{os.getcwd()}:/var/task",
        "--platform",
        "linux/amd64",
        "--entrypoint",
        "",
        "public.ecr.aws/lambda/python:3.12",
        "/bin/sh",
        "-c",
        "pip install --target /var/task/lambda-package -r /var/task/requirements.txt --platform manylinux2014_x86_64 --only-binary=:all: --upgrade",
    ]

    local_cmd = [
        "python",
        "-m",
        "pip",
        "install",
        "--target",
        "lambda-package",
        "-r",
        "requirements.txt",
        "--platform",
        "manylinux2014_x86_64",
        "--implementation",
        "cp",
        "--python-version",
        "3.12",
        "--only-binary=:all:",
        "--upgrade",
    ]

    if docker_available():
        print("Using Docker-based dependency build.")
        subprocess.run(docker_cmd, check=True)
        return

    print("Docker is unavailable. Falling back to local cross-platform pip build.")
    subprocess.run(local_cmd, check=True)


def main() -> None:
    print("Creating Lambda deployment package...")

    if os.path.exists("lambda-package"):
        shutil.rmtree("lambda-package")
    if os.path.exists("lambda-deployment.zip"):
        os.remove("lambda-deployment.zip")

    os.makedirs("lambda-package")

    install_dependencies()

    print("Copying application files...")
    for file in ["server.py", "lambda_handler.py", "context.py", "resources.py", "resoruces.py"]:
        if os.path.exists(file):
            shutil.copy2(file, "lambda-package/")

    if os.path.exists("data"):
        shutil.copytree("data", "lambda-package/data")

    print("Creating zip file...")
    with zipfile.ZipFile("lambda-deployment.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("lambda-package"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "lambda-package")
                zipf.write(file_path, arcname)

    size_mb = os.path.getsize("lambda-deployment.zip") / (1024 * 1024)
    print(f"Created lambda-deployment.zip ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()


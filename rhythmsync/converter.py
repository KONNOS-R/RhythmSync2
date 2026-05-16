import subprocess


#converts audio file to other formats
def convert(input_file, output_file):
    try:
        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", input_file,
            output_file
        ], check=True)

        print(f"Converted successfully:")
        print(f"{input_file} -> {output_file}")

    except FileNotFoundError:
        print("FFmpeg is not installed.")

    except subprocess.CalledProcessError:
        print("Conversion failed.")
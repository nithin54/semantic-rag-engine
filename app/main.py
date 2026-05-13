import sys
from app.benchmark import benchmark
from app.web_server import run_server


def main():
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == 'server' or mode == 'web':
            run_server(debug=True, port=5000)
        elif mode == 'benchmark' or mode == 'cli':
            benchmark()
        else:
            print("Usage: python -m app.main [server|web|benchmark|cli]")
            print("  server/web    - Start Flask web dashboard on localhost:5000")
            print("  benchmark/cli - Run CLI benchmark only")
    else:
        # Default: start web server
        run_server(debug=True, port=5000)


if __name__ == "__main__":
    main()

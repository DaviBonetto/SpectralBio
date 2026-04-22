FROM python:3.11-slim

WORKDIR /workspace

RUN pip install --no-cache-dir uv

COPY . /workspace

RUN uv sync --frozen

CMD ["uv", "run", "spectralbio", "preflight", "--json", "--cpu-only", "--offline"]

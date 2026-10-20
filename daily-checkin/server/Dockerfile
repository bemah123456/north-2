# The check-in server, for hosting it somewhere phones can reach over HTTPS.
#   docker build -t checkin-server .
#   docker run -p 8000:8000 -v checkin-data:/srv/data -e API_TOKEN=... checkin-server
# Add --build-arg LOCAL_STT=1 for free speech-to-text on the server
# (Whisper, needs about 2 GB more), then run it with -e STT_PROVIDER=local.
FROM python:3.13-slim

ARG LOCAL_STT=0
WORKDIR /srv
COPY requirements.txt requirements-local.txt ./
RUN if [ "$LOCAL_STT" = "1" ]; then \
      apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/* && \
      pip install --no-cache-dir -r requirements-local.txt; \
    else \
      pip install --no-cache-dir -r requirements.txt; \
    fi
COPY checkin ./checkin

# The database and recordings live here; mount a volume so they survive restarts.
VOLUME /srv/data
EXPOSE 8000
CMD ["uvicorn", "checkin.api:app", "--host", "0.0.0.0", "--port", "8000"]

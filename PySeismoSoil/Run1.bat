docker build -t seismo .
docker run -e folder_name=medium -e sheet_name=Vs450 -v .:/app seismo
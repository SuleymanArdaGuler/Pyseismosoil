docker build -t seismo .
docker run -e folder_name=bigger -e sheet_name=Vs450 -v .:/app seismo
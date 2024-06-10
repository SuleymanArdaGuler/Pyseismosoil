docker build -t seismo .
docker run -e folder_name=low -e sheet_name=Vs150 -v .:/app seismo



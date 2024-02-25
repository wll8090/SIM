api=container_api_sim
image_api=image_api_sim
banco=container_mysql_sim

help:
	@echo run, stop, criar_image, del_image, log
app_run:
	docker run -d --name $(api) --link $(banco) -v./:/main/ $(image_api)
i_app_run:
	docker run -it --name $(api) --link $(banco) -v./:/main/ $(image_api) bash
app_stop:
	docker rm -f $(api)
app_log:
	docker logs $(api)

app_criar_image:
	docker build -t $(image_api) .

app_del_image:
	docker image rm -f $(image_api)

app_update:
	make app_stop
	make app_run



mysql_run:
	docker run --name $(banco) -v ./../mysql:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=root -d mysql

mysql_stop:
	docker rm -f $(banco)

mysql_log:
	docker logs $(banco)

mysql_interative:
	docker exec -it $(banco) mysql -u root -p

mysql_gerate_banco:
	docker run -it --name $(api) --link $(banco) -v./:/main/ $(image_api) python3 conexao_db.py


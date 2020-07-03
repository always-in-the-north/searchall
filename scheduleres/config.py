from typing import Union

_config_data = {}

_config_data.update({
	"error_count": 3,

	# mysql db
	"db_host":"localhost",
	"db_port":3306,
	"db_user":"root",
	"db_password":"123456",
	"db_dbname": "mysql",

	# proxies
	"db_path": "./db/scylla.db",
	"db_path_qiushibaike": "./db/qiushibaike.db",
	"db_proxies_count": 10,

	#download
	"retrytimes": 3,
	"resleeptime": 3,
	"maxsizequeue": 10,
	""

	"end":""
	})


def get_config(key: str, default: str = None) -> Union[str, None]:
    try:
        return _config_data[key]
    except KeyError:
        return default
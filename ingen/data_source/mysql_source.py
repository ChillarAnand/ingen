import logging
import time

from mysql.connector import connection

from ingen.data_source.source import DataSource
from ingen.reader.mysql_reader import MYSQLReader
from ingen.utils.properties import Properties
from ingen.utils.sql_query_parser import SqlQueryParser

log = logging.getLogger()


class MYSQLSource(DataSource):
    """
    This class represents mysql database source
    """

    _connection = None

    def __init__(self, source, params_map=None):
        """
        Loads a MYSQLSource
        :param source: Map which contains source data such as id, query, etc.
        :param params_map: Map which contains runtime parameters such as query_params, run_date
        """
        super().__init__(source['id'])
        self._src_data_checks = source.get('src_data_checks', [])
        self._host = Properties.get_property('datasource.mysql.host')
        self._user = Properties.get_property('datasource.mysql.user')
        self._password = Properties.get_property('datasource.mysql.password')
        self._database = source.get('database')
        self._query = SqlQueryParser().parse_query(source['query'], params_map, source.get('temp_table_params'))
        if self._connection is None:
            self._connection = connection.MySQLConnection(host=self._host,
                                                          user=self._user,
                                                          password=self._password,
                                                          database=self._database)
        else:
            raise Exception('You cannot create another MySQL connection')

    def fetch(self):
        """
        Executes the SQL query
        :return: A DataFrame created using the result of the query
        """
        reader = MYSQLReader(self._connection)
        start = time.time()
        data = reader.execute(self._query)
        end = time.time()
        log.info(f"Successfully fetched data from mysql in {end - start:.2f} seconds.")
        return data

    def fetch_validations(self):
        """
        Method to fetch validations from the source
        :return: list of dictionaries containing mentioned validations on all columns
        """
        return self._src_data_checks
# -*- coding: utf-8 -*-


class SgLazyResultSet(object):

    """
    Fetch results from shotgun lazily
    """

    def __init__(
        self,
        connection,
        entity_type,
        filters,
        fields=None,
        order=None,
        filter_operator=None,
        limit=0,
        retired_only=False,
        page=0
    ):
        self._connection = connection
        self._entity_type = entity_type
        self._sg_find_args = {
            'entity_type': entity_type,
            'filters': filters,
            'fields': fields,
            'order': order,
            'filter_operator': filter_operator,
            'limit': limit,
            'retired_only': retired_only,
            'page': page
        }

        self.__dict__['_data'] = []

    def __len__(self):
        """
        Get result_set's length with a summary
        """
        if not hasattr(self, '_summaries'):
            self._summaries = self._connection.connection().summarize(
                entity_type=self._entity_type,
                filters=[],
                summary_fields=[{'field': 'id', 'type': 'count'}]
            ).get('summaries')
        return self._summaries.get('id')

    def __getitem__(self, key):
        if isinstance(key, slice):
            _sg_find_args = self._sg_find_args.copy()
            start, stop, step = key.start, key.stop, key.step
            slice_limit = stop - start
            slice_page = start / slice_limit
            # if slice_limit > _sg_find_args.get('limit'):
            #raise Exception("out of bounds", _sg_find_args.get('limit'))
            _sg_find_args['limit'] = slice_limit
            _sg_find_args['page'] = slice_page
            query = self._connection._sg_find(**_sg_find_args)
            return [self._connection._createEntity(self._entity_type, data)
                    for data in query]
        else:
            query = self._connection._sg_find(
                self._entity_type, self.filters, self.fields)
            return self._connection._createEntity(self._entity_type, query[key])

    def to_list(self):
        return self._data

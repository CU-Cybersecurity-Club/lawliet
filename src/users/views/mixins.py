"""
Various mixins used for class-based views on the site
"""

import abc

from typing import Optional

"""
JSON REST API class definitions
"""


class JsonAPIError(Exception):
    """
    An exception that should be thrown whenever there's an error making
    a request to the site's REST API.
    """

    def __init__(self, msg: str, *args, status_code: int = 400, **kwargs):
        super().__init__(msg, *args, **kwargs)
        self.status_code = status_code


class JsonResponseMixin(metaclass=abc.ABCMeta):
    def render_to_json_response(self, get_params: dict, context: Optional[dict] = None):
        """
        Return a JSON response, using 'context' to create the payload.
        """

        try:
            status_code = 200

            if context is not None:
                query_results = self.get_data(get_params, context=context)
            else:
                # Don't pass in the context kwarg so that child classes
                # can use their own defaults.
                query_results = self.get_data(get_params)

            if isinstance(query_results, QuerySet):
                query_results = serializers.serialize("json", query_results)
            elif isinstance(query_results, str):
                # Assume that the string is already JSON-formatted
                pass
            else:
                query_results = json.dumps(query_results)

        except JsonAPIError as ex:
            # Error processing the query
            status_code = ex.status_code
            query_results = json.dumps({"error": str(ex)})

        return HttpResponse(
            query_results, content_type="application/json", status=status_code,
        )

    @abc.abstractmethod
    def get_data(
        self, get_params: dict, context: Optional[dict] = None,
    ) -> Union[Dict, QuerySet, str]:
        """
        Given a context, make a query to the database. Use the results of
        the query in the response.
        """
        pass

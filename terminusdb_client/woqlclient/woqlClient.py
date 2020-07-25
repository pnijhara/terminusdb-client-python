# woqlClient.py
import copy

from ..__version__ import __version__
from .api_endpoint_const import APIEndpointConst
from .connectionCapabilities import ConnectionCapabilities

# from .errorMessage import *
from .connectionConfig import ConnectionConfig
from .dispatchRequest import DispatchRequest

# from .errors import (InvalidURIError)
# from .errors import doc, opts

# WOQL client object
# license Apache Version 2
# summary Python module for accessing the Terminus DB API


class WOQLClient:
    def __init__(self, server_url, **kwargs):
        # current conCapabilities context variables
        """The WOQLClient constructor.

        Parameters
        ----------
        server_url : str
            URL of the server that this client will connect to.
        \**kwargs
            Configuration options used to construct a :class:`ConnectionConfig` instance.
        """
        self.conConfig = ConnectionConfig(server_url, **kwargs)
        self.conCapabilities = ConnectionCapabilities()

    def connect(self, **kwargs):
        """Connect to a Terminus server at the given URI with an API key.

        Stores the terminus:ServerCapability document returned
        in the conCapabilities register which stores, the url, key, capabilities,
        and database meta-data for the connected server.

        If the ``serverURL`` argument is omitted,
        :attr:`self.conConfig.serverURL` will be used if present
        or an error will be raise.

        Parameters
        ----------
        \**kwargs
            Configuration options added to :attr:`conConfig`.

        Returns
        -------
        dict or raise an InvalidURIError.

        Examples
        -------
        >>> woql.WOQLClient().connect(serverUrl, key)
        dict
        """
        if len(kwargs) > 0:
            self.conConfig.update(**kwargs)

        json_obj = self.dispatch(APIEndpointConst.CONNECT, self.conConfig.server)
        self.conCapabilities.set_capabilities(json_obj)
        return json_obj

    def copy(self):
        return copy.deepcopy(self)

    def basic_auth(self, key=None, user=None):
        if key:
            self.conConfig.set_basic_auth(key, user)
        return self.conConfig.basic_auth

    def remote_auth(self, auth_info=None):
        if type(auth_info) == dict:
            self.conConfig.set_remote_auth(auth_info)
        return self.conConfig.remote_auth

    def set_db(self, dbid):
        return self.db(dbid)

    def db(self, dbid=None):
        if dbid:
            self.conConfig.db = dbid
        return self.conConfig.db

    def account(self, accountid=None):
        if accountid:
            self.conConfig.account = accountid
        return self.conConfig.account

    def user_account(self):
        u = self.conCapabilities.get_user()
        return u.id

    def user(self):
        return self.conCapabilities.get_user()

    def repo(self, repoid=None):
        if repoid:
            self.conConfig.repo = repoid

        return self.conConfig.repo

    def ref(self, refid=None):
        if refid:
            self.conConfig.ref = refid
        return self.conConfig.ref

    def checkout(self, branchid=None):
        if branchid:
            self.conConfig.branch = branchid
        return self.conConfig.branch

    def uid(self, ignore_jwt=True):
        return self.conConfig.user(ignore_jwt)

    def resource(self, ttype, val=None):
        """Create a resource identifier string based on the current config.

        Parameters
        ----------
        ttype : str
            Type of resource. One of ["db", "meta", "repo", "commits", "ref", "branch"].
        val : str, optional
            Branch or commit identifier.

        Returns
        -------
        str
            The constructed resource string.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.account("<account>")
        '<account>'
        >>> client.db("<db>")
        '<db>'
        >>> client.repo("<repo>")
        '<repo>'
        >>> client.resource("db")
        '<account>/<db>/'
        >>> client.resource("meta")
        '<account>/<db>/_meta'
        >>> client.resource("commits")
        '<account>/<db>/<repo>/_commits'
        >>> client.resource("repo")
        '<account>/<db>/<repo>/_meta'
        >>> client.resource("ref", "<reference>")
        '<account>/<db>/<repo>/commit/<reference>'
        >>> client.resource("branch", "<branch>")
        '<account>/<db>/<repo>/branch/<branch>'
        """
        base = self.account() + "/" + self.db() + "/"
        if type == "db":
            return base
        elif type == "meta":
            return base + "_meta"
        base = base + self.repo()
        if type == "repo":
            return base + "/_meta"
        elif type == "commits":
            return base + "/_commits"
        if val is None:
            if ttype == "ref":
                val = self.ref()
            else:
                val = self.checkout()
        if ttype == "branch":
            return base + "/branch/" + val
        if ttype == "ref":
            return base + "/commit/" + val

    def set(self, **kwargs):  # bad naming
        self.conConfig.update(**kwargs)

    def create_database(
        self,
        dbid,
        accountid,
        label=None,
        description=None,
        prefixes=None,
        include_schema=True,
    ):
        """Create a TerminusDB database by posting
        a terminus:Database document to the Terminus Server.

        Parameters
        ----------
        dbid : str
            Unique identifier of the database.
        accountid : str
            Account identifier.
        label : str, optional
            Database name.
        description : str, optional
            Database description.
        prefixes
            TODO
        include_schema : bool
            TODO

        Returns
        -------
        dict

        Examples
        --------
        >>> client = WOQLClient(server="http://localhost:6363")
        >>> client..createDatabase("someDB", "Database Label", "password")
        """
        details = {}
        # if no prefixes, we will add default here
        if prefixes is None:
            details["prefixes"] = {
                "scm": f"terminusdb://{accountid}/{dbid}/schema#",
                "doc": f"terminusdb://{accountid}/{dbid}/data/",
            }

        if label:
            details["label"] = label
        if description:
            details["comment"] = description

        self.db(dbid)
        self.account(accountid)

        if include_schema:
            response = self.dispatch(
                APIEndpointConst.CREATE_DATABASE, self.conConfig.db_url(), details
            )
            self.create_graph(
                "schema",
                "main",
                f"Python client {__version__} message: Creating schema graph",
            )
            return response

        return self.dispatch(
            APIEndpointConst.CREATE_DATABASE, self.conConfig.db_url(), details
        )

    def delete_database(self, dbid, accountid=None):
        """Delete a TerminusDB database.

        If ``accountid`` is provided, then the account in the config will be updated
        and the new value will be used in future requests to the server.

        Parameters
        ----------
        dbid : str
            Identifier of the database to delete.
        accountid : str, optional
            Optional account identifier.

        Returns
        -------
        dict

        Examples
        -------
        >>> client = WOQLClient(server="http://localhost:6363")
        >>> client.deleteDatabase("someDBToDelete", "password")
        dict
        """

        self.db(dbid)
        if accountid:
            self.account(accountid)

        json_response = self.dispatch(
            APIEndpointConst.DELETE_DATABASE, self.conConfig.db_url()
        )
        return json_response

    def create_graph(self, graph_type, graph_id, commit_msg):
        if graph_type in ["inference", "schema", "instance"]:
            commit = self._generate_commit(commit_msg)
            return self.dispatch(
                APIEndpointConst.CREATE_GRAPH,
                self.conConfig.graph_url(graph_type, graph_id),
                commit,
            )

        raise ValueError(
            "Create graph parameter error - you must specify a valid graph_type (inference, instance, schema), graph_id and commit message"
        )

    def delete_graph(self, graph_type, graph_id, commit_msg):
        if graph_type in ["inference", "schema", "instance"]:
            commit = self._generate_commit(commit_msg)
            return self.dispatch(
                APIEndpointConst.DELETE_GRAPH,
                self.conConfig.graph_url(graph_type, graph_id),
                commit,
            )

        raise ValueError(
            "Delete graph parameter error - you must specify a valid graph_type (inference, instance, schema), graph_id and commit message"
        )

    def get_triples(self, graph_type, graph_id):
        return self.dispatch(
            APIEndpointConst.GET_TRIPLES,
            self.conConfig.triples_url(graph_type, graph_id),
        )

    def update_triples(self, graph_type, graph_id, turtle, commit_msg):
        commit = self._generate_commit(commit_msg)
        commit.turtle = turtle
        return self.dispatch(
            APIEndpointConst.UPDATE_TRIPLES,
            self.conConfig.triples_url(graph_type, graph_id),
            commit,
        )

    def get_class_frame(self, class_name):
        opts = {"class": class_name}
        return self.dispatch(
            APIEndpointConst.CLASS_FRAME,
            self.conConfig.class_frame_url(class_name),
            opts,
        )

    def query(self, woql_query, commit_msg=None, file_list=None):
        if (
            hasattr(woql_query, "_contains_update_check")
            and woql_query._contains_update_check()
        ):
            if not commit_msg:
                commit_msg = f"Update Query generated by python client {__version__}"
            query_obj = self._generate_commit(commit_msg)
        elif type(woql_query) == dict and commit_msg:
            query_obj = self._generate_commit(commit_msg)
        else:
            query_obj = {}
        if type(woql_query) != dict and hasattr(woql_query, "to_dict"):
            woql_query = woql_query.to_dict()
        woql_query["@context"] = self.conCapabilities.get_context_for_outbound_query(
            None, self.db()
        )
        if type(file_list) == dict:
            file_dict = query_obj
            for name in file_list:
                path = file_list[name]
                stream = open(path, "rb")
                file_dict[name] = (name, stream, "text/plain")
            file_dict["query"] = (
                None,
                woql_query,
                "application/json",
            )
            payload = None
        else:
            file_dict = None
            query_obj["query"] = woql_query
            payload = query_obj

        return self.dispatch(
            APIEndpointConst.WOQL_QUERY, self.conConfig.query_url(), payload, file_dict
        )

    def branch(self, new_branch_id):
        if self.ref():
            source = {
                "origin": f"{self.account()}/{self.db()}/{self.repo()}/commit/{self.ref()}"
            }
        else:
            source = {
                "origin": f"{self.account()}/{self.db()}/{self.repo()}/branch/{self.checkout()}"
            }

        return self.dispatch(
            APIEndpointConst.BRANCH, self.conConfig.branch_url(new_branch_id), source
        )

    def pull(self, remote_source_repo):
        rc_args = self._prepare_revision_control_args(remote_source_repo)
        if rc_args and rc_args.get("remote") and rc_args.get("remote_branch"):
            return self.dispatch(
                APIEndpointConst.PULL, self.conConfig.pull_url(), rc_args
            )
        else:
            raise ValueError(
                "Pull parameter error - you must specify a valid remote source and branch to pull from"
            )

    def fetch(self, remote_source_repo):
        rc_args = self._prepare_revision_control_args(remote_source_repo)
        if rc_args and rc_args.get("remote") and rc_args.get("remote_branch"):
            return self.dispatch(
                APIEndpointConst.FETCH, self.conConfig.fetch_url(), rc_args
            )
        else:
            raise ValueError(
                "Fetch parameter error - you must specify a valid remote source and branch to pull from"
            )

    def push(self, remote_target_repo):
        rc_args = self._prepare_revision_control_args(remote_target_repo)
        if rc_args and rc_args.get("remote") and rc_args.get("remote_branch"):
            return self.dispatch(
                APIEndpointConst.PUSH, self.conConfig.push_url(), rc_args
            )
        else:
            raise ValueError(
                "Push parameter error - you must specify a valid remote target"
            )

    def rebase(self, rebase_source):
        rc_args = self._prepare_revision_control_args(rebase_source)
        if rc_args and rc_args.get("rebase_from"):
            return self.dispatch(
                APIEndpointConst.REBASE, self.conConfig.rebase_url(), rc_args
            )
        else:
            raise ValueError(
                "Rebase parameter error - you must specify a valid rebase source to rebase from"
            )

    def clonedb(self, clone_source, newid):
        rc_args = self._prepare_revision_control_args(clone_source)
        if rc_args and rc_args.get("remote_url"):
            return self.dispatch(
                APIEndpointConst.CLONE, self.conConfig.clone_url(newid), rc_args
            )
        else:
            raise ValueError(
                "Clone parameter error - you must specify a valid id for the cloned database"
            )

    def _generate_commit(self, msg, author=None):
        if author:
            mes_author = author
        else:
            mes_author = self.conCapabilities.author()

        ci = {"commit_info": {"author": mes_author, "message": msg}}
        return ci

    def _prepare_revision_control_args(self, rc_args=None):
        if rc_args is None:
            return False
        if not rc_args.get("author"):
            rc_args["author"] = self.conCapabilities.author()
        return rc_args

    def dispatch(
        self, action, url, payload=None, file_dict=None
    ):  # don't use dict as default
        """Directly dispatch to a TerminusDB database.

        Parameters
        ----------
        action
            The action to perform on the server.
        url : str
            The server URL to point the action at.
        payload : dict
            Payload to send to the server.
        file_dict : list, optional
            List of files to include in the query.

        Returns
        -------
        dict or raise an InvalidURIError.
        """

        # check if we can perform this action or raise an AccessDeniedError error
        # review the access control
        # self.conCapabilities.capabilitiesPermit(action)
        # url, action, payload={}, basic_auth, jwt=None, file_dict=None)
        if payload is None:
            payload = {}
        return DispatchRequest.send_request_by_action(
            url, action, payload, self.basic_auth(), self.remote_auth(), file_dict
        )

    def get_metadata(self, dbid, account):
        return self.conCapabilities.get_database(dbid, account)

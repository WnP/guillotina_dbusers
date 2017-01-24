from plone.server.api.service import Service
from plone.server.browser import Response
from plone.server.utils import get_authenticated_user
from plone.server.json.interfaces import IResourceSerializeToJson
from zope.component import queryMultiAdapter
from plone.server import configure
from plone.server.interfaces import ISite


@configure.service(
    context=ISite,
    name="@user_info",
    method="GET",
    permission="plone.Authenticated")
class Info(Service):

    async def __call__(self):
        user = get_authenticated_user(self.request)
        serializer = queryMultiAdapter((user, self.request), IResourceSerializeToJson)
        if serializer:
            data = serializer()
        else:
            data = {}
        data.update({
            'id': user.id,
            'roles': user._roles,
            'groups': getattr(user, '_groups', [])
        })
        return Response(data)

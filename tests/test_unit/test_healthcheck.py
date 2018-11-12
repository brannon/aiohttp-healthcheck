import json
import unittest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp_healthcheck import HealthCheck, EnvironmentDump


class BasicHealthCheckTest(AioHTTPTestCase):
    path = '/h'

    def setUp(self):
        self.hc = HealthCheck()
        super().setUp()

    def get_app(self):
        app = web.Application()
        app.router.add_get(self.path, self.hc)
        return app

    @unittest_run_loop
    async def test_basic_check(self):
        response = await self.client.get(self.path)
        self.assertEqual(200, response.status)

    @unittest_run_loop
    async def test_failing_check(self):
        async def fail_check():
            return False, "FAIL"

        self.hc.add_check(fail_check)
        response = await self.client.get(self.path)
        self.assertEqual(500, response.status)

    @unittest_run_loop
    async def test_sync_check(self):
        def test_check():
            return True, "OK"

        self.hc.add_check(test_check)
        response = await self.client.get(self.path)
        self.assertEqual(200, response.status)


class BasicEnvironmentDumpTest(AioHTTPTestCase):
    path = '/e'

    def setUp(self):
        self.hc = EnvironmentDump()
        super().setUp()

    def get_app(self):
        app = web.Application()
        app.router.add_get(self.path, self.hc)
        return app

    @unittest_run_loop
    async def test_basic_check(self):
        async def test_ok():
            return "OK"

        self.hc.add_section("test_func", test_ok)

        response = await self.client.get(self.path)
        self.assertEqual(200, response.status)
        jr = await response.json()
        self.assertEqual("OK", jr["test_func"])

    @unittest_run_loop
    async def test_sync_check(self):
        def test_ok():
            return "OK"

        self.hc.add_section("test_func", test_ok)

        response = await self.client.get(self.path)
        self.assertEqual(200, response.status)
        jr = await response.json()
        self.assertEqual("OK", jr["test_func"])


if __name__ == '__main__':
    unittest.main()

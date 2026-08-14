from django.test import SimpleTestCase
from unittest.mock import patch

from utility.response_handler import HttpResponse
from users.service.userService import UserService
from utils.constants import ROLE_MANAGEMENT_SCOPE, ROLES


class UserEmployeeResponseHandlerTests(SimpleTestCase):
	@patch('users.service.userService.User.objects.filter')
	def test_build_unique_username_appends_suffix_for_duplicate_default(self, filter_mock):
		service = UserService()
		filter_mock.return_value.exists.side_effect = [True, False]

		username = service.build_unique_username('super_admin')

		self.assertEqual(username, 'super_admin_1')

	def test_build_default_username_sanitizes_name(self):
		service = UserService()

		username = service.build_default_username('Super', 'Admin')

		self.assertEqual(username, 'super_admin')

	def test_vertical_admin_can_manage_all_api_roles_except_super_admin(self):
		vertical_scope = ROLE_MANAGEMENT_SCOPE[ROLES.VERTICAL_ADMIN.value]

		self.assertIn(ROLES.LOAN_OFFICER.value, vertical_scope)
		self.assertIn(ROLES.BRANCH_MANAGER.value, vertical_scope)
		self.assertIn(ROLES.TELE_USER.value, vertical_scope)
		self.assertNotIn(ROLES.VERTICAL_ADMIN.value, vertical_scope)
		self.assertNotIn(ROLES.SUPER_ADMIN.value, vertical_scope)

	def test_service_explicitly_blocks_vertical_admin_from_managing_vertical_admin(self):
		service = UserService()

		self.assertFalse(
			service.can_manage_role(ROLES.VERTICAL_ADMIN.value, ROLES.VERTICAL_ADMIN.value)
		)

	def test_create_user_blocks_vertical_admin_from_creating_vertical_admin(self):
		service = UserService()

		response = service.create_user(
			data={"role": ROLES.VERTICAL_ADMIN.value},
			actor_role=ROLES.VERTICAL_ADMIN.value,
		)

		self.assertEqual(response["status_code"], 403)
		self.assertEqual(response["status"], "error")
		self.assertEqual(
			response["data"],
			{"msg": "VERTICAL_ADMIN cannot create VERTICAL_ADMIN role user."},
		)

	def test_super_admin_cannot_create_vertical_admin_via_api(self):
		service = UserService()

		response = service.create_user(
			data={"role": ROLES.VERTICAL_ADMIN.value},
			actor_role=ROLES.SUPER_ADMIN.value,
		)

		self.assertEqual(response["status_code"], 403)
		self.assertEqual(response["status"], "error")
		self.assertEqual(
			response["data"],
			{"msg": "VERTICAL_ADMIN cannot create VERTICAL_ADMIN role user."},
		)

	def test_create_user_requires_actor_role(self):
		service = UserService()

		response = service.create_user(
			data={"role": ROLES.VERTICAL_ADMIN.value},
			actor_role=None,
		)

		self.assertEqual(response["status_code"], 403)
		self.assertEqual(response["status"], "error")
		self.assertEqual(response["data"], {"msg": "Unauthorized to create users"})

	def test_super_admin_message_matches_business_rule(self):
		service = UserService()

		self.assertEqual(
			service.get_immutable_role_message("TELE_USER", "SUPER_ADMIN"),
			"SUPER_ADMIN is the master user and can be created only once from backend.",
		)

	def test_vertical_admin_message_matches_business_rule(self):
		service = UserService()

		self.assertEqual(
			service.get_immutable_role_message("TELE_USER", "VERTICAL_ADMIN"),
			"TELE_USER cannot create VERTICAL_ADMIN role user.",
		)

	def test_created_response_preserves_http_201(self):
		response = HttpResponse().response(201, {"user_id": "abc123"})

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["status"], "success")
		self.assertEqual(response.data["status_code"], 201)
		self.assertEqual(response.data["data"], {"user_id": "abc123"})

	def test_forbidden_response_preserves_http_403(self):
		response = HttpResponse().response(
			403,
			{"msg": "SUPER_ADMIN is the master user and can be created only once from backend."},
			error_msg={"msg": "SUPER_ADMIN is the master user and can be created only once from backend."},
			error_code=403,
		)

		self.assertEqual(response.status_code, 403)
		self.assertEqual(response.data["status"], "error")
		self.assertEqual(response.data["status_code"], 403)
		self.assertEqual(response.data["data"], {"msg": "SUPER_ADMIN is the master user and can be created only once from backend."})

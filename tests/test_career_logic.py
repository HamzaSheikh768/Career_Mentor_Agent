import unittest
from unittest.mock import AsyncMock, call, patch

from career_service import (
    CareerGuidance,
    build_career_guidance,
    format_guidance_markdown,
    normalize_career_title,
    safe_provider_error_message,
)
from roadmaps_tools import lookup_career_roadmap, normalize_career_key


class CareerLogicTests(unittest.TestCase):
    def test_provider_auth_error_does_not_expose_secret(self) -> None:
        class FakeProviderError(Exception):
            status_code = 403

        fake_secret = "fake-secret-that-must-never-be-shown"
        message = safe_provider_error_message(FakeProviderError(fake_secret))

        self.assertNotIn(fake_secret, message)
        self.assertNotIn("api_key", message.lower())
        self.assertIn("credentials", message)

    def test_unknown_provider_error_does_not_expose_details(self) -> None:
        fake_secret = "another-fake-secret"
        message = safe_provider_error_message(RuntimeError(fake_secret))

        self.assertNotIn(fake_secret, message)
        self.assertIn("couldn’t create your plan", message)

    def test_provider_unavailable_error_has_retry_guidance(self) -> None:
        class FakeProviderError(Exception):
            status_code = 503

        message = safe_provider_error_message(FakeProviderError("provider details"))

        self.assertIn("temporarily busy", message)
        self.assertIn("try again", message)
        self.assertNotIn("provider details", message)

    def test_roadmap_lookup_is_case_insensitive(self) -> None:
        roadmap = lookup_career_roadmap("Data Scientist")
        self.assertIn("Python", roadmap)
        self.assertNotIn("No stored roadmap", roadmap)

    def test_roadmap_key_normalizes_punctuation(self) -> None:
        self.assertEqual(normalize_career_key("UI/UX Designer"), "ui ux designer")

    def test_unknown_roadmap_has_useful_fallback(self) -> None:
        self.assertIn("professional knowledge", lookup_career_roadmap("Urban Planner"))

    def test_career_title_removes_model_label(self) -> None:
        self.assertEqual(normalize_career_title("Career: Data Scientist"), "Data Scientist")

    def test_markdown_contains_all_sections(self) -> None:
        output = format_guidance_markdown(
            CareerGuidance("Data Scientist", "1. Learn Python", "- Junior Data Analyst")
        )
        self.assertIn("Data Scientist", output)
        self.assertIn("Skill roadmap", output)
        self.assertIn("Roles to explore", output)


class CareerFallbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_transient_primary_failure_uses_fallback_model(self) -> None:
        class FakeProviderError(Exception):
            status_code = 503

        primary_runtime = object()
        fallback_runtime = object()
        expected = CareerGuidance("Data Scientist", "Learn Python", "Data Analyst")

        with (
            patch.dict(
                "os.environ",
                {
                    "GEMINI_MODEL": "gemini-3.8-flash",
                    "GEMINI_FALLBACK_MODEL": "gemini-3.6-flash",
                },
            ),
            patch("career_service.get_runtime") as get_runtime,
            patch(
                "career_service._build_with_runtime", new_callable=AsyncMock
            ) as build_with_runtime,
        ):
            get_runtime.side_effect = [primary_runtime, fallback_runtime]
            build_with_runtime.side_effect = [FakeProviderError(), expected]

            result = await build_career_guidance("coding and mathematics")

        self.assertEqual(result, expected)
        self.assertEqual(get_runtime.call_args_list, [call(), call("gemini-3.6-flash")])
        self.assertEqual(build_with_runtime.await_count, 2)


if __name__ == "__main__":
    unittest.main()

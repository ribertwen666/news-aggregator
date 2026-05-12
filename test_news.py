import unittest
from ranker import deduplicate, normalize_title
from display import format_article
from fetcher import Article


class TestArticle(unittest.TestCase):
    def test_article_creation(self):
        a = Article(title="Test", url="https://example.com",
                    source="雪球", category="stock", score=80.0,
                    summary="这是一条摘要")
        self.assertEqual(a.title, "Test")
        self.assertEqual(a.category, "stock")
        self.assertEqual(a.score, 80.0)
        self.assertEqual(a.summary, "这是一条摘要")


class TestNormalizeTitle(unittest.TestCase):
    def test_removes_punctuation(self):
        result = normalize_title("重磅！A股大涨，沪指突破3500点？")
        self.assertNotIn("！", result)
        self.assertNotIn("？", result)

    def test_strips_whitespace(self):
        self.assertEqual(normalize_title("  华为发布新芯片  "), "华为发布新芯片")

    def test_lowercase(self):
        result = normalize_title("AI改变世界")
        self.assertEqual(result, "ai改变世界")


class TestDeduplicate(unittest.TestCase):
    def test_identical_titles_merge(self):
        a1 = Article("华为发布新手机", "url1", "源1", "tech", 90)
        a2 = Article("华为发布新手机", "url2", "源2", "tech", 80)
        result = deduplicate([a1, a2])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].score, 90)

    def test_similar_titles_merge(self):
        a1 = Article("A股三大指数集体大涨收涨超2%", "url1", "雪球", "stock", 85)
        a2 = Article("A股三大指数集体大涨，收涨超2%", "url2", "华尔街见闻", "stock", 75)
        result = deduplicate([a1, a2])
        self.assertEqual(len(result), 1)

    def test_different_titles_keep_both(self):
        a1 = Article("华为发布新手机", "url1", "源1", "tech", 90)
        a2 = Article("苹果发布新电脑", "url2", "源2", "tech", 80)
        result = deduplicate([a1, a2])
        self.assertEqual(len(result), 2)


class TestFormatArticle(unittest.TestCase):
    def test_format_includes_category_and_title(self):
        a = Article("测试新闻标题", "https://test.com",
                    "测试源", "finance", 90)
        result = format_article(a, 0)
        self.assertIn("测试新闻标题", result)
        self.assertIn("测试源", result)

    def test_format_stock_category(self):
        a = Article("股票新闻", "url", "雪球", "stock", 90)
        result = format_article(a, 0)
        self.assertIn("股票新闻", result)


if __name__ == "__main__":
    unittest.main()

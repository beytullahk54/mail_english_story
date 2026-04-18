import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from .models import BlogPost, BlogPostCreate, BlogPostItem, BlogPostDetail, BlogListResponse

SAMPLE_POSTS = [
    {
        "title": "Why Reading Short Stories is the Best Way to Learn English",
        "title_tr": "Kısa Hikaye Okumak İngilizce Öğrenmenin En İyi Yolu",
        "slug": "why-reading-stories-best-way-learn-english",
        "excerpt": "Discover why reading short, level-appropriate stories is one of the most effective and enjoyable methods for learning English as a second language.",
        "excerpt_tr": "Seviyenize uygun kısa hikayeler okumanın, İngilizce öğrenmenin en etkili ve keyifli yöntemlerinden biri olduğunu keşfedin.",
        "meta_description": "Learn why reading short stories is the best method for English language learning. Discover how story-based learning improves vocabulary, grammar, and fluency naturally.",
        "meta_description_tr": "Kısa hikaye okumanın İngilizce öğrenmek için neden en iyi yöntem olduğunu öğrenin.",
        "author": "English Story Team",
        "tags": json.dumps(["learning", "stories", "tips", "vocabulary"]),
        "cover_image": None,
        "published": True,
        "content": """<p>When it comes to learning English, textbooks and grammar exercises have their place — but nothing comes close to the power of reading stories. Whether you're a complete beginner or an intermediate learner looking to break through a plateau, short stories offer a uniquely effective learning experience.</p>

<h2>Learning in Context, Not in Isolation</h2>
<p>One of the biggest challenges with traditional methods is that vocabulary and grammar are taught in isolation. You memorize a word list on Monday and forget half of it by Friday. Stories solve this problem by presenting new words and structures <strong>in context</strong> — embedded in a narrative that gives them meaning and makes them memorable.</p>
<p>When you read "The old lighthouse keeper squinted against the salty wind," you don't just learn the word "squint." You feel it. That emotional connection is what makes vocabulary stick.</p>

<h2>Comprehensible Input: The Engine of Language Acquisition</h2>
<p>Linguist Stephen Krashen's influential theory of <em>comprehensible input</em> argues that we acquire language most naturally when we understand messages that are just slightly beyond our current level — what he calls "i+1." Short, level-matched stories are a perfect vehicle for this. They expose you to new patterns without overwhelming you.</p>

<h2>Building Reading Fluency</h2>
<p>Fluency isn't just about speaking — it starts with reading. As you encounter the same grammatical structures repeatedly across different stories, your brain begins to recognize and process them automatically. This reduces cognitive load and frees you to focus on meaning rather than decoding.</p>

<h2>Motivation Matters</h2>
<p>Perhaps most importantly, stories are <em>enjoyable</em>. Engagement is the single biggest predictor of language learning success. When you're genuinely interested in what happens next, you read more. When you read more, you learn faster. It's a virtuous cycle.</p>

<h2>How English Story Uses This Approach</h2>
<p>Every story in our platform is carefully calibrated to your CEFR level (A1 through B2) and delivered daily to your inbox. You'll never feel bored by material that's too easy, or frustrated by content that's too hard. Just right-level stories, every day, building your English naturally over time.</p>

<p>Ready to experience the difference? <a href="/">Subscribe and get your first story today</a>.</p>""",
    },
    {
        "title": "Understanding CEFR Levels: What A1, A2, B1, B2 Mean for You",
        "slug": "understanding-cefr-levels-a1-a2-b1-b2-explained",
        "excerpt": "Confused by language level labels? This guide breaks down the CEFR framework — A1, A2, B1, B2 — and helps you understand exactly where you stand and where you're headed.",
        "meta_description": "A clear guide to CEFR language levels A1, A2, B1, and B2. Find out what each level means, what skills you need, and how to progress from beginner to upper-intermediate English.",
        "author": "English Story Team",
        "tags": json.dumps(["cefr", "levels", "beginner", "intermediate", "a1", "a2", "b1", "b2"]),
        "cover_image": None,
        "published": True,
        "content": """<p>If you've ever searched for English courses, language apps, or learning materials, you've almost certainly seen labels like "A1," "B2," or "upper-intermediate." These come from the <strong>Common European Framework of Reference for Languages</strong> (CEFR) — an internationally recognized standard for describing language ability.</p>

<p>Understanding where you sit on this scale can help you choose the right materials, set realistic goals, and measure your progress objectively.</p>

<h2>The CEFR Scale at a Glance</h2>
<p>The framework is divided into six levels across three broad bands:</p>
<ul>
  <li><strong>A (Basic User):</strong> A1 (Beginner) and A2 (Elementary)</li>
  <li><strong>B (Independent User):</strong> B1 (Intermediate) and B2 (Upper-Intermediate)</li>
  <li><strong>C (Proficient User):</strong> C1 (Advanced) and C2 (Mastery)</li>
</ul>

<h2>A1 — Absolute Beginner</h2>
<p>At A1, you can introduce yourself, ask and answer simple personal questions, and understand very basic sentences about familiar topics. Think: "My name is Elif. I am from Turkey. I like coffee."</p>
<p>Stories at this level use high-frequency vocabulary, short sentences, and simple present tense.</p>

<h2>A2 — Elementary</h2>
<p>At A2, you can handle routine situations like shopping, ordering food, or describing your daily routine. You understand short, clear texts on familiar topics. Grammar starts to expand — past tense, comparatives, and simple questions.</p>

<h2>B1 — Intermediate</h2>
<p>This is a major milestone. At B1, you can deal with most situations likely to arise while travelling in an English-speaking country. You can write simple connected texts on familiar topics and describe experiences, events, and plans. Stories become more complex, with richer vocabulary and more varied grammar structures.</p>

<h2>B2 — Upper-Intermediate</h2>
<p>At B2, you can read and understand the main ideas of complex texts on both concrete and abstract topics, including technical discussions in your field of specialisation. You interact with a degree of fluency and spontaneity that makes conversation with native speakers quite natural.</p>

<h2>Which Level Are You?</h2>
<p>Not sure? A rough self-check: if you can read this article comfortably without looking up many words, you're likely at B1 or above. If some sentences require re-reading, you're probably A2-B1. If this feels very challenging, start at A1 or A2.</p>

<p>Our platform lets you choose your level when you subscribe, and our AI-generated stories adapt to each level's vocabulary and grammar complexity. <a href="/">Sign up to start reading at your level today</a>.</p>""",
    },
    {
        "title": "How AI Generates Personalized English Stories for Every Level",
        "slug": "how-ai-generates-personalized-english-stories",
        "excerpt": "Behind every story you receive is a sophisticated AI system that crafts level-appropriate narratives. Here's how it works — and why it's better than static textbook content.",
        "meta_description": "Learn how artificial intelligence generates personalized English learning stories for A1 to B2 levels. Discover the technology behind AI-powered language learning content.",
        "author": "English Story Team",
        "tags": json.dumps(["ai", "technology", "personalization", "gemini"]),
        "cover_image": None,
        "published": True,
        "content": """<p>Every story you receive from English Story isn't pulled from a database or written by a human author — it's created fresh by an AI, specifically tailored to your proficiency level. But what does that actually mean, and why does it matter for your learning?</p>

<h2>The Challenge with Static Content</h2>
<p>Traditional English learning materials have a fundamental problem: they're static. A textbook written for A2 learners in 2010 uses the same examples, the same vocabulary lists, and the same stories year after year. Learners get bored. Worse, the content doesn't adapt to individual interests or current vocabulary needs.</p>

<h2>Enter Large Language Models</h2>
<p>Modern AI language models — the same technology behind tools like ChatGPT and Google's Gemini — have an extraordinary ability to generate coherent, grammatically accurate text on virtually any topic. More importantly, they can be instructed to respect specific linguistic constraints: "use only A1-level vocabulary," "keep sentences under 10 words," or "include exactly 3 uses of the past simple tense."</p>
<p>This is precisely what happens every time English Story generates a story for you.</p>

<h2>Level-Calibrated Generation</h2>
<p>For each level, our system provides the AI with detailed instructions:</p>
<ul>
  <li><strong>A1:</strong> Maximum sentence length of 8 words, top-500 most common English words, simple present and present continuous only.</li>
  <li><strong>A2:</strong> Simple past and future included, sentences up to 12 words, familiar everyday situations.</li>
  <li><strong>B1:</strong> Varied tenses, phrasal verbs, relative clauses, and idiomatic expressions introduced gradually.</li>
  <li><strong>B2:</strong> Complex sentence structures, passive voice, conditionals, and sophisticated vocabulary in context.</li>
</ul>

<h2>Fresh Every Day</h2>
<p>Because stories are generated on demand, every subscriber receives unique content. There's no risk of reading the same story twice, and topics stay varied — travel, technology, friendship, mystery, science — keeping learning fresh and engaging.</p>

<h2>Illustrated with AI Art</h2>
<p>Each story also receives a custom AI-generated illustration, making the reading experience more immersive and supporting visual learners who benefit from associating images with vocabulary.</p>

<p>The result is a learning experience that feels more like enjoying a good book than studying a textbook — because that's exactly what it should feel like. <a href="/">Subscribe and see for yourself</a>.</p>""",
    },
    {
        "title": "5 Daily Habits to Accelerate Your English Learning",
        "slug": "5-daily-habits-to-accelerate-english-learning",
        "excerpt": "Consistency beats intensity every time. These five simple daily habits — each taking less than 15 minutes — will compound into dramatic English improvement over weeks and months.",
        "meta_description": "Five proven daily habits that accelerate English language learning. Science-backed tips for vocabulary building, listening practice, and reading that fit into any schedule.",
        "author": "English Story Team",
        "tags": json.dumps(["habits", "tips", "learning", "daily-practice", "vocabulary"]),
        "cover_image": None,
        "published": True,
        "content": """<p>The biggest myth in language learning is that you need hours of daily study to make progress. In reality, <strong>short, consistent exposure</strong> beats marathon sessions every time. Here are five habits that fit into even the busiest schedule — and deliver real results.</p>

<h2>1. Read One Story Every Morning (10 minutes)</h2>
<p>Start your day with an English story at your level. Morning reading sets a positive tone, and your brain is particularly receptive to new information after sleep. Reading for comprehension — not translation — trains your brain to think in English rather than mentally converting from your native language.</p>
<p><em>Tip: Don't look up every unknown word. Try to guess meaning from context first. Only look up words that appear 3+ times and you still can't understand.</em></p>

<h2>2. Keep a Vocabulary Journal (5 minutes)</h2>
<p>After reading, write down 3-5 new words or phrases you encountered. Don't just write the definition — write an example sentence you create yourself. This active recall and production dramatically improves retention compared to passive reading alone.</p>

<h2>3. Listen While You Commute</h2>
<p>Swap music or podcasts for English audio content during your commute or exercise time. Even passive listening at your level trains your ear to the rhythm, intonation, and natural speed of the language. BBC Learning English, podcasts for learners, and audiobooks at your level all work well.</p>

<h2>4. Think in English for 5 Minutes</h2>
<p>This sounds strange, but it's incredibly powerful. Choose a mundane activity — washing dishes, walking to the kitchen — and narrate it in your head in English. "I'm opening the refrigerator. The milk is on the left shelf. I need to buy more eggs." This builds fluency pathways without requiring any materials.</p>

<h2>5. Review Before Bed (5 minutes)</h2>
<p>Flip through your vocabulary journal before sleep. Research shows that memory consolidation happens during sleep, and material reviewed just before bed is more likely to be retained. A 5-minute review is more effective than an hour of study at noon.</p>

<h2>The Compound Effect</h2>
<p>None of these habits is dramatic on its own. But practiced daily for 3-6 months, they compound into something remarkable. Vocabulary expands naturally. Reading speed increases. Comprehension deepens. And crucially, English starts to feel less like a subject and more like a skill you actually have.</p>

<p>Start with just the first habit — a daily story. <a href="/">Subscribe to English Story and get a level-appropriate story in your inbox every day</a>.</p>""",
    },
    {
        "title": "The Science Behind Learning English Through Storytelling",
        "slug": "science-learning-english-through-storytelling",
        "excerpt": "Storytelling isn't just an ancient human tradition — it's a neurologically privileged form of communication. Here's what brain science tells us about why stories make language learning so effective.",
        "meta_description": "Discover the neuroscience behind story-based language learning. Explore how narrative activates the brain, improves memory, and accelerates English vocabulary acquisition.",
        "author": "English Story Team",
        "tags": json.dumps(["science", "neuroscience", "storytelling", "memory", "research"]),
        "cover_image": None,
        "published": True,
        "content": """<p>Humans have told stories for at least 30,000 years — long before writing, formal education, or language apps. There's a reason for that. Our brains are, at a fundamental level, <em>story-processing machines</em>. And modern neuroscience is revealing exactly why this makes storytelling one of the most powerful vehicles for language learning.</p>

<h2>Neural Coupling: Brains in Sync</h2>
<p>Princeton neuroscientist Uri Hasson and his team discovered that when a person tells a story and another person listens, their brain activity actually synchronizes. The same regions light up in both brains — a phenomenon called <em>neural coupling</em>. The closer the coupling, the better the communication and comprehension.</p>
<p>This synchronization doesn't happen when people process lists of facts or grammar rules. It's specific to narrative. Which suggests the brain has a privileged channel for stories — one that language learners can tap into.</p>

<h2>The Neurochemistry of Engagement</h2>
<p>When we're engaged in a compelling story, our brains release <strong>dopamine</strong> — the neurotransmitter associated with anticipation and reward. Dopamine doesn't just feel good; it also acts as a memory consolidator. Information encoded during high-dopamine states is remembered far more effectively than information processed during neutral states.</p>
<p>This is why you can remember the plot of a film you saw once five years ago, but struggle to recall vocabulary you studied last week.</p>

<h2>Embodied Simulation</h2>
<p>Reading about an action activates many of the same neural regions as physically performing that action — a phenomenon called <em>embodied simulation</em>. When you read "She gripped the cold door handle," your somatosensory cortex partially activates as if you were gripping something cold yourself.</p>
<p>For language learners, this means vocabulary encountered in narrative context is encoded not just linguistically, but also sensorially and emotionally — creating multiple retrieval pathways in memory.</p>

<h2>The Advantage of Narrative Structure</h2>
<p>Stories have a predictable structure: characters, conflict, resolution. This structure gives learners a scaffolding that makes new language more predictable and therefore more comprehensible. Unknown words become guessable from narrative context, reducing the anxiety that often blocks learning.</p>

<h2>Putting Science into Practice</h2>
<p>The implications are clear: if you want to learn English efficiently, read stories at your level — regularly and with genuine engagement. Don't just study the language; experience it.</p>
<p>English Story exists to make that experience as effortless as possible: AI-crafted stories at exactly your level, delivered daily, so the science works for you automatically. <a href="/">Start your story journey today</a>.</p>""",
    },
]


class BlogService:
    def _to_item(self, post: BlogPost) -> BlogPostItem:
        return BlogPostItem(
            id=post.id,
            title=post.title,
            title_tr=post.title_tr,
            slug=post.slug,
            slug_tr=post.slug_tr,
            excerpt=post.excerpt,
            excerpt_tr=post.excerpt_tr,
            author=post.author,
            cover_image=post.cover_image,
            tags=json.loads(post.tags) if post.tags else [],
            published_at=post.published_at,
        )

    def _to_detail(self, post: BlogPost) -> BlogPostDetail:
        return BlogPostDetail(
            id=post.id,
            title=post.title,
            title_tr=post.title_tr,
            slug=post.slug,
            slug_tr=post.slug_tr,
            excerpt=post.excerpt,
            excerpt_tr=post.excerpt_tr,
            content=post.content,
            content_tr=post.content_tr,
            author=post.author,
            cover_image=post.cover_image,
            tags=json.loads(post.tags) if post.tags else [],
            meta_description=post.meta_description,
            meta_description_tr=post.meta_description_tr,
            published_at=post.published_at,
        )

    def get_posts(
        self, db: Session, page: int = 1, page_size: int = 10, tag: str | None = None
    ) -> BlogListResponse:
        query = db.query(BlogPost).filter(BlogPost.published == True)  # noqa: E712
        if tag:
            query = query.filter(BlogPost.tags.contains(f'"{tag}"'))
        total = query.count()
        posts = (
            query.order_by(BlogPost.published_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return BlogListResponse(items=[self._to_item(p) for p in posts], total=total, page=page, page_size=page_size)

    def get_post_by_slug(self, db: Session, slug: str) -> BlogPostDetail | None:
        # Search both English and Turkish slugs
        from sqlalchemy import or_
        post = db.query(BlogPost).filter(
            or_(BlogPost.slug == slug, BlogPost.slug_tr == slug),
            BlogPost.published == True  # noqa: E712
        ).first()
        return self._to_detail(post) if post else None

    def create_post(self, db: Session, data: BlogPostCreate) -> BlogPost:
        post = BlogPost(
            title=data.title,
            slug=data.slug,
            excerpt=data.excerpt,
            content=data.content,
            author=data.author,
            cover_image=data.cover_image,
            tags=json.dumps(data.tags) if data.tags else None,
            meta_description=data.meta_description,
            published=data.published,
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    def seed_posts(self, db: Session) -> int:
        existing = db.query(BlogPost).count()
        if existing > 0:
            return 0
        for data in SAMPLE_POSTS:
            db.add(BlogPost(**data))
        db.commit()
        return len(SAMPLE_POSTS)

INTENT_QUESTIONS = {
    "Research & Insights": [
        {"name": "topic", "description": "The main subject of the research.", "is_mandatory": True, "example": "Current trends in sustainable fashion"},
        {"name": "industry", "description": "The specific industry or market sector.", "is_mandatory": True, "example": "Apparel & Fashion"},
        {"name": "target_audience", "description": "Who the research is focused on.", "is_mandatory": True, "example": "Gen Z consumers"},
        {"name": "competitors", "description": "Key competitors to analyze.", "is_mandatory": True, "example": "Patagonia, Everlane"},
        {"name": "key_questions", "description": "Specific questions the research must answer.", "is_mandatory": True, "example": "What materials are Gen Z most likely to pay a premium for?"},
        {"name": "geographic_focus", "description": "The region the research should focus on.", "is_mandatory": True, "example": "North America"},
        {"name": "objective", "description": "The ultimate goal of gathering this research.", "is_mandatory": True, "example": "To inform our Q4 product roadmap"},
        {"name": "preferred_sources", "description": "Specific types of sources or websites to look at.", "is_mandatory": False, "example": "Industry reports, Vogue business"},
        {"name": "timeframe", "description": "The time period of data to look at.", "is_mandatory": False, "example": "Last 2 years"},
        {"name": "format_requirements", "description": "How the research should be presented.", "is_mandatory": False, "example": "Summary with bullet points"}
    ],
    "Concept Ideation": [
        {"name": "product_name", "description": "The name of the product or service.", "is_mandatory": True, "example": "EcoSneak 500"},
        {"name": "core_problem", "description": "The main problem this solves for the user.", "is_mandatory": True, "example": "Uncomfortable, non-breathable eco-friendly shoes"},
        {"name": "unique_selling_proposition", "description": "What makes this different from competitors.", "is_mandatory": True, "example": "Made from 100% recycled ocean plastic but feels like memory foam"},
        {"name": "target_audience", "description": "Who this concept is for.", "is_mandatory": True, "example": "Urban commuters aged 25-40"},
        {"name": "brand_archetype", "description": "The personality of the brand.", "is_mandatory": True, "example": "The Explorer / The Rebel"},
        {"name": "key_emotion", "description": "The feeling the concept should evoke.", "is_mandatory": True, "example": "Freedom, lightness, responsibility"},
        {"name": "objective", "description": "What this concept needs to achieve.", "is_mandatory": True, "example": "Launch a new product category"},
        {"name": "budget_tier", "description": "General budget constraint.", "is_mandatory": False, "example": "High/Premium"},
        {"name": "competitor_references", "description": "Brands to use as inspiration or to avoid.", "is_mandatory": False, "example": "Avoid Allbirds minimalist style, go for Nike aggressive styling"},
        {"name": "format_needs", "description": "Specific outputs needed.", "is_mandatory": False, "example": "3 big ideas with taglines"}
    ],
    "Copywriting": [
        {"name": "objective", "description": "The main goal of the copy.", "is_mandatory": True, "example": "Drive email signups"},
        {"name": "target_audience", "description": "Who will be reading this copy.", "is_mandatory": True, "example": "Small business owners"},
        {"name": "tone_of_voice", "description": "How the copy should sound.", "is_mandatory": True, "example": "Professional but conversational, witty"},
        {"name": "key_message", "description": "The single most important takeaway.", "is_mandatory": True, "example": "Our software saves you 10 hours a week."},
        {"name": "call_to_action", "description": "What the user should do next.", "is_mandatory": True, "example": "Start your 14-day free trial"},
        {"name": "product_features", "description": "Specific features to mention.", "is_mandatory": True, "example": "Automated invoicing, tax calculations"},
        {"name": "format_and_length", "description": "Where this will live and how long it should be.", "is_mandatory": True, "example": "Landing page hero section, under 50 words"},
        {"name": "seo_keywords", "description": "Keywords to include for search.", "is_mandatory": False, "example": "best accounting software, automated taxes"},
        {"name": "brand_guidelines", "description": "Words to use or avoid.", "is_mandatory": False, "example": "Do not use the word 'cheap', use 'affordable'."},
        {"name": "references", "description": "Links to existing copy or inspiration.", "is_mandatory": False, "example": "Make it sound like Mailchimp's homepage."}
    ],
    "Visual Moodboards": [
        {"name": "project_goal", "description": "What the moodboard is for.", "is_mandatory": True, "example": "Redesigning the company website"},
        {"name": "target_audience", "description": "Who the visuals need to appeal to.", "is_mandatory": True, "example": "High net-worth individuals"},
        {"name": "core_aesthetic", "description": "The overall look and feel.", "is_mandatory": True, "example": "Minimalist, quiet luxury, dark mode"},
        {"name": "color_palette", "description": "Expected colors or tones.", "is_mandatory": True, "example": "Charcoal grey, gold accents, deep emerald"},
        {"name": "typography_style", "description": "Desired font styles.", "is_mandatory": True, "example": "Elegant serif headers, clean sans-serif body"},
        {"name": "imagery_type", "description": "What kind of photos or illustrations.", "is_mandatory": True, "example": "High contrast black and white photography, architectural edges"},
        {"name": "brand_personality", "description": "The vibe the brand gives off.", "is_mandatory": True, "example": "Exclusive, sophisticated, timeless"},
        {"name": "competitor_styles", "description": "Visuals to emulate or avoid.", "is_mandatory": False, "example": "Emulate Aesop, avoid anything too colorful or loud."},
        {"name": "cultural_references", "description": "Movies, art, or eras to pull from.", "is_mandatory": False, "example": "1990s minimalist fashion, brutalist architecture"},
        {"name": "specific_assets_needed", "description": "What needs to be included.", "is_mandatory": False, "example": "Include textures and some UI element examples."}
    ],
    "Product Renders": [
        {"name": "product_type", "description": "What is being rendered.", "is_mandatory": True, "example": "A smart coffee mug"},
        {"name": "core_materials", "description": "What the product is made of.", "is_mandatory": True, "example": "Matte black ceramic, brushed steel base"},
        {"name": "lighting_style", "description": "How the scene should be lit.", "is_mandatory": True, "example": "Cinematic side-lighting, dramatic shadows"},
        {"name": "environment_setting", "description": "Where the product is placed.", "is_mandatory": True, "example": "On a dark oak desk next to a laptop, modern office"},
        {"name": "camera_angle", "description": "How the product is viewed.", "is_mandatory": True, "example": "Eye-level close up, shallow depth of field"},
        {"name": "key_features_to_highlight", "description": "Specific parts of the product to show.", "is_mandatory": True, "example": "The glowing LED temperature indicator on the side"},
        {"name": "color_palette", "description": "Colors of the product and scene.", "is_mandatory": True, "example": "Monochrome with a pop of neon blue from the LED"},
        {"name": "aspect_ratio", "description": "The dimensions of the final image.", "is_mandatory": False, "example": "16:9 widescreen"},
        {"name": "vibe_and_mood", "description": "The feeling the render should give.", "is_mandatory": False, "example": "Futuristic, sleek, productive"},
        {"name": "reference_images", "description": "What it should look similar to.", "is_mandatory": False, "example": "Like an Apple product announcement render."}
    ],
    "Campaign Strategy": [
        {"name": "campaign_objective", "description": "What the campaign needs to achieve.", "is_mandatory": True, "example": "Drive 10,000 app downloads in Q3"},
        {"name": "target_audience", "description": "Who the campaign is targeting.", "is_mandatory": True, "example": "Fitness enthusiasts aged 18-35"},
        {"name": "core_value_proposition", "description": "Why the audience should care.", "is_mandatory": True, "example": "The only fitness app that adapts to your daily energy levels"},
        {"name": "primary_channels", "description": "Where the campaign will live.", "is_mandatory": True, "example": "Instagram, TikTok, and App Store Ads"},
        {"name": "budget_allocation", "description": "How money is divided.", "is_mandatory": True, "example": "$50k total, 70% Social, 30% Search"},
        {"name": "timeline", "description": "When things happen.", "is_mandatory": True, "example": "Teaser in June, Launch in July, Sustaining in August"},
        {"name": "key_performance_indicators", "description": "How success is measured.", "is_mandatory": True, "example": "Cost Per Install (CPI), Click-Through Rate (CTR)"},
        {"name": "competitor_campaigns", "description": "What competitors are doing.", "is_mandatory": False, "example": "MyFitnessPal just launched a similar feature, we need to beat their messaging."},
        {"name": "influencer_strategy", "description": "If and how creators will be used.", "is_mandatory": False, "example": "Partnering with micro-influencers in the yoga space."},
        {"name": "phasing", "description": "Different stages of the campaign.", "is_mandatory": False, "example": "Phase 1: Awareness, Phase 2: Conversion, Phase 3: Retention"}
    ],
    "Social Media Execution": [
        {"name": "platform", "description": "Which social network.", "is_mandatory": True, "example": "TikTok"},
        {"name": "content_format", "description": "What type of post.", "is_mandatory": True, "example": "15-second short form video"},
        {"name": "objective", "description": "Goal of the post.", "is_mandatory": True, "example": "Engagement and viral reach"},
        {"name": "target_audience", "description": "Who should see this.", "is_mandatory": True, "example": "College students"},
        {"name": "key_message", "description": "What the post must say.", "is_mandatory": True, "example": "Get 50% off student discount before Friday."},
        {"name": "visual_concept", "description": "What happens in the visual/video.", "is_mandatory": True, "example": "POV: you just found out about the discount while cramming for finals."},
        {"name": "call_to_action", "description": "What the user should do.", "is_mandatory": True, "example": "Click link in bio"},
        {"name": "audio_or_trend", "description": "Specific sounds or trends to use.", "is_mandatory": False, "example": "Use the trending 'Oh No' audio."},
        {"name": "hashtags", "description": "Tags to include.", "is_mandatory": False, "example": "#studentlife #discount #finalsweek"},
        {"name": "posting_time", "description": "When to publish.", "is_mandatory": False, "example": "Thursday at 7PM EST"}
    ],
    "Brand Positioning": [
        {"name": "brand_name", "description": "The name of the company or product.", "is_mandatory": True, "example": "Luminary Skincare"},
        {"name": "current_perception", "description": "How people currently see the brand.", "is_mandatory": True, "example": "Old-fashioned, expensive, clinical"},
        {"name": "desired_perception", "description": "How people SHOULD see the brand.", "is_mandatory": True, "example": "Science-backed but accessible and modern"},
        {"name": "target_audience", "description": "Who the brand is for.", "is_mandatory": True, "example": "Millennials looking for preventative anti-aging"},
        {"name": "core_values", "description": "What the brand stands for.", "is_mandatory": True, "example": "Transparency, efficacy, cruelty-free"},
        {"name": "unique_selling_proposition", "description": "What makes it different.", "is_mandatory": True, "example": "Medical-grade ingredients at drugstore prices."},
        {"name": "brand_archetype", "description": "The character of the brand.", "is_mandatory": True, "example": "The Sage / The Caregiver"},
        {"name": "competitors", "description": "Who the brand is fighting against.", "is_mandatory": False, "example": "The Ordinary, CeraVe"},
        {"name": "brand_voice", "description": "How the brand speaks.", "is_mandatory": False, "example": "Educating, warm, no-nonsense."},
        {"name": "visual_identity_cues", "description": "Colors or styles associated with it.", "is_mandatory": False, "example": "Clean white, stark black text, very minimal."}
    ]
}

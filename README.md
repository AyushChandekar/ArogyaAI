# Healthcare Education Chatbot 🏥🤖

A multilingual AI chatbot designed to provide healthcare education for rural and semi-urban populations. Built with Rasa and MarianMT for seamless multilingual support.

## Features ✨

- **Multilingual Support**: English, Hindi, Bengali, Tamil, Telugu, Gujarati, Kannada, Malayalam, Marathi, Punjabi, and more
- **Disease Information**: Comprehensive details about symptoms, prevention, and treatment guidance
- **Vaccination Schedules**: Age-specific immunization information for all life stages
- **Outbreak Alerts**: Information about disease outbreaks and emergency procedures
- **Medical Disclaimers**: Always includes appropriate medical disclaimers
- **User-Friendly**: Simple language suitable for limited health literacy

## Target Audience 👥

- **Age Range**: 15 years to elderly individuals
- **Geographic Focus**: Rural and semi-urban populations
- **Health Literacy**: Limited to moderate
- **Languages**: Primary English with multilingual capabilities

## Project Structure 📁

```
healthChatbot/
├── actions/
│   └── actions.py              # Custom Rasa actions
├── data/
│   ├── nlu.yml                 # NLU training data
│   ├── stories.yml             # Conversation stories
│   └── rules.yml               # Conversation rules
├── config.yml                  # Rasa configuration
├── domain.yml                  # Chatbot domain definition
├── endpoints.yml               # Endpoint configurations
├── credentials.yml             # Channel credentials
├── healthcare_knowledge.py     # Healthcare knowledge base
├── translation_service.py      # Multilingual translation service
├── test_healthcare_chatbot.py  # Comprehensive test suite
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation 🚀

### Prerequisites

- Python 3.8 or higher
- At least 4GB RAM (for translation models)
- Internet connection (for initial model downloads)

### Setup Instructions

1. **Clone or Download the Project**
   ```bash
   cd C:\Users\ayush\ayush_files\python\healthChatbot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the Rasa Model**
   ```bash
   rasa train
   ```

4. **Start the Action Server** (in a separate terminal)
   ```bash
   rasa run actions
   ```

5. **Start the Rasa Server**
   ```bash
   rasa run --enable-api --cors "*"
   ```

6. **Test the Chatbot**
   ```bash
   rasa shell
   ```

## Usage Examples 💬

### English Conversations
```
User: Hello
Bot: Hello! I'm Arogya, your friendly health education companion...

User: What are the symptoms of dengue?
Bot: Here's important information about Dengue Fever:
     🔸 Key Symptoms:
     1. High fever (104°F/40°C)
     2. Severe headache
     ...

User: When should babies get vaccinated?
Bot: 💉 Vaccination Schedule for 6 weeks - 12 months:
     1. DPT: 6, 10, 14 weeks
     ...
```

### Multilingual Support
```
User: आप हिंदी बोल सकते हैं?
Bot: हाँ, मैं हिंदी में बात कर सकता हूँ...

User: ডেঙ্গুর লক্ষণ কি?
Bot: ডেঙ্গু জ্বর সম্পর্কে গুরুত্বপূর্ণ তথ্য...
```

## Available Intents 🎯

### Health Information
- `ask_disease_info`: Get information about diseases
  - Example: "What are the symptoms of malaria?"
  - Entities: disease (dengue, malaria, covid-19, diabetes, etc.)

- `ask_vaccination_schedule`: Get vaccination schedules
  - Example: "When should children get vaccinated?"
  - Entities: age_group (infants, children, adults, elderly, etc.)

- `ask_outbreak_info`: Get outbreak information
  - Example: "Is there a disease outbreak in Mumbai?"
  - Entities: location (city names, regions)

### General Interactions
- `greet`: Greeting messages
- `goodbye`: Farewell messages
- `thanks`: Thank you messages
- `ask_languages`: Ask about language support
- `bot_challenge`: Ask if it's a bot
- `out_of_scope`: Handle non-health topics

## Supported Diseases 🦠

- **Viral**: Dengue, COVID-19, Influenza
- **Bacterial**: Tuberculosis (TB)
- **Parasitic**: Malaria
- **Chronic**: Diabetes, Hypertension (High Blood Pressure)
- **And more**: The system supports aliases like 'covid', 'corona', 'tb', 'bp', 'sugar'

## Supported Age Groups 👶👴

- **Newborn** (0-6 weeks)
- **Infants** (6 weeks - 12 months)
- **Children** (12 months - 5 years)
- **Adults** (18+ years)
- **Pregnant Women**
- **Elderly** (60+ years)

## Translation Capabilities 🌍

### Supported Languages
- **English** (en) - Primary
- **Hindi** (hi) - हिंदी
- **Bengali** (bn) - বাংলা
- **Tamil** (ta) - தமிழ்
- **Telugu** (te) - తెలుగు
- **Gujarati** (gu) - ગુજરાતી
- **Kannada** (kn) - ಕನ್ನಡ
- **Malayalam** (ml) - മലയാളം
- **Marathi** (mr) - मराठी
- **Punjabi** (pa) - ਪੰਜਾਬੀ
- **Urdu** (ur) - اردو

### Translation Models
- Uses Helsinki-NLP MarianMT models
- Automatic language detection
- Fallback to English for unsupported languages
- Context-aware healthcare translations

## Testing 🧪

### Run Comprehensive Tests
```bash
python test_healthcare_chatbot.py
```

### Test Categories
- **Healthcare Knowledge**: Disease info, vaccination schedules
- **Translation Service**: Language detection, multilingual support
- **Conversation Flows**: Complete interaction scenarios
- **Error Handling**: Edge cases and invalid inputs
- **Integration Tests**: Full system functionality
- **Medical Disclaimers**: Proper disclaimer inclusion

### Sample Test Results
```
==============================
TEST RESULTS SUMMARY
==============================
Total Tests: 24
Successful: 24
Failures: 0
Errors: 0
Success Rate: 100.0%
==============================
```

## Configuration ⚙️

### Rasa Configuration (`config.yml`)
- Optimized NLU pipeline for healthcare domain
- Character-level and word-level features
- DIET classifier for entity recognition
- Fallback handling with appropriate thresholds

### Domain Configuration (`domain.yml`)
- Healthcare-specific intents and entities
- Multilingual slots for user language preferences
- Response templates with medical disclaimers
- Custom actions for dynamic responses

## API Integration 🔌

### REST API Endpoints
```
POST http://localhost:5005/webhooks/rest/webhook
Content-Type: application/json

{
  "sender": "user123",
  "message": "What are the symptoms of dengue?"
}
```

### Response Format
```json
[
  {
    "recipient_id": "user123",
    "text": "Here's important information about Dengue Fever:\n\n🔸 Key Symptoms:\n1. High fever (104°F/40°C)\n2. Severe headache\n...\n\nRemember, this is general information. Always consult a healthcare professional for personal medical advice."
  }
]
```

## Deployment Options 🚀

### Local Development
```bash
rasa run actions &
rasa run --enable-api --cors "*"
```

### Production Deployment
1. **Docker Deployment**
   ```dockerfile
   FROM rasa/rasa:latest
   COPY . /app
   WORKDIR /app
   RUN rasa train
   CMD ["run", "--enable-api", "--cors", "*"]
   ```

2. **Cloud Deployment**
   - Deploy on AWS, GCP, or Azure
   - Use container orchestration (Kubernetes)
   - Configure load balancing for high availability

### Channel Integration
- **Web Widget**: Embed in healthcare websites
- **WhatsApp**: Via Twilio or official WhatsApp Business API
- **Facebook Messenger**: Direct integration
- **Telegram**: Bot integration
- **SMS**: Via Twilio or similar services

## Performance Considerations 📈

### Memory Usage
- Base Rasa model: ~500MB
- Translation models: ~1-2GB (lazy loaded)
- Recommended RAM: 4GB+

### Response Times
- Simple queries: <1 second
- Translation required: 2-5 seconds
- Complex medical queries: 3-7 seconds

### Optimization Tips
- Preload common translation models
- Use caching for frequent queries
- Implement response compression
- Consider model quantization for production

## Medical Disclaimer ⚠️

**Important**: This chatbot provides general health education information only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for:

- Specific medical concerns
- Personal health conditions
- Treatment decisions
- Emergency situations
- Medication advice

## Contributing 🤝

### Development Guidelines
1. Follow the healthcare prompt specifications
2. Maintain medical accuracy and disclaimers
3. Test multilingual functionality
4. Update knowledge base with verified information
5. Ensure cultural sensitivity

### Adding New Diseases
1. Update `healthcare_knowledge.py`
2. Add NLU examples in `data/nlu.yml`
3. Create test cases
4. Verify medical accuracy

### Adding New Languages
1. Update `translation_service.py`
2. Add language mappings
3. Test translation quality
4. Update documentation

## Troubleshooting 🔧

### Common Issues

1. **Translation Models Not Loading**
   ```bash
   # Manually download models
   python -c "from transformers import MarianMTModel, MarianTokenizer; MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-en-hi')"
   ```

2. **Memory Issues**
   - Increase system RAM
   - Use model quantization
   - Implement lazy loading

3. **Slow Response Times**
   - Preload translation models
   - Use SSD storage
   - Optimize model parameters

4. **Action Server Connection**
   ```bash
   # Check if action server is running
   curl http://localhost:5055/health
   ```

## Support & Contact 📞

For technical support, medical content verification, or deployment assistance:

- **Technical Issues**: Create GitHub issues
- **Medical Content**: Consult healthcare professionals
- **Deployment**: Follow cloud provider documentation

## License 📄

This project is designed for educational and humanitarian purposes. Please ensure compliance with local healthcare regulations and data privacy laws when deploying.

---

**Version**: 1.0.0  
**Last Updated**: September 2025  
**Developed with**: ❤️ for global healthcare education

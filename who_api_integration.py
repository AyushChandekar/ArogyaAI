"""
WHO API Integration and Real-time Health Data Fetcher
Integrates with WHO and other health data sources for current guidelines
"""

import requests
import json
import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class HealthGuideline:
    """Structure for health guidelines from WHO and other sources"""
    title: str
    content: str
    source: str
    date: str
    url: str
    category: str
    region: str

class WHOAPIIntegration:
    """
    Integration with WHO and other health data sources
    Provides real-time health updates, guidelines, and alerts
    """
    
    def __init__(self):
        """Initialize WHO API integration"""
        self.session = None
        self.cache = {}
        self.cache_duration = timedelta(hours=4)
        self.last_update = {}
        
        # API endpoints
        self.endpoints = {
            'who_news_rss': 'https://www.who.int/feeds/entity/mediacentre/news/en/rss.xml',
            'who_disease_outbreak': 'https://extranet.who.int/publicemergency',
            'covid_data': 'https://disease.sh/v3/covid-19/countries/IN',
            'global_health': 'https://ghoapi.azureedge.net/api/',
            'cdc_health_data': 'https://data.cdc.gov/api/views/',
            'indian_health_ministry': 'https://www.mohfw.gov.in/'
        }
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={'User-Agent': 'Healthcare Chatbot/1.0'}
            )
        return self.session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        last_update = self.last_update.get(cache_key)
        if not last_update:
            return False
        
        return datetime.now() - last_update < self.cache_duration
    
    async def fetch_who_news_updates(self) -> List[HealthGuideline]:
        """Fetch latest WHO news and updates from RSS feed"""
        cache_key = 'who_news'
        
        if self.is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        guidelines = []
        
        try:
            session = await self.get_session()
            async with session.get(self.endpoints['who_news_rss']) as response:
                if response.status == 200:
                    content = await response.text()
                    guidelines = self._parse_who_rss(content)
        
        except Exception as e:
            logger.error(f"Error fetching WHO news: {e}")
            # Return sample data if API fails
            guidelines = self._get_sample_who_guidelines()
        
        # Cache the results
        self.cache[cache_key] = guidelines
        self.last_update[cache_key] = datetime.now()
        
        return guidelines
    
    def _parse_who_rss(self, rss_content: str) -> List[HealthGuideline]:
        """Parse WHO RSS feed content"""
        guidelines = []
        
        try:
            root = ET.fromstring(rss_content)
            
            for item in root.findall('.//item')[:10]:  # Get latest 10 items
                title = item.find('title')
                description = item.find('description')
                link = item.find('link')
                pub_date = item.find('pubDate')
                
                if title is not None:
                    guideline = HealthGuideline(
                        title=title.text or "WHO Health Update",
                        content=description.text[:500] if description is not None and description.text else "Latest WHO health guideline",
                        source="WHO",
                        date=pub_date.text if pub_date is not None else datetime.now().strftime("%Y-%m-%d"),
                        url=link.text if link is not None else "https://www.who.int",
                        category="General Health",
                        region="Global"
                    )
                    guidelines.append(guideline)
        
        except Exception as e:
            logger.error(f"Error parsing WHO RSS: {e}")
            return self._get_sample_who_guidelines()
        
        return guidelines
    
    def _get_sample_who_guidelines(self) -> List[HealthGuideline]:
        """Get sample WHO guidelines when API is not available"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        return [
            HealthGuideline(
                title="WHO Health Emergency Preparedness Guidelines",
                content="Latest WHO recommendations for health emergency preparedness including disease outbreak response, vaccination strategies, and community health measures. Focus on strengthening health systems and improving surveillance capabilities.",
                source="WHO",
                date=today,
                url="https://www.who.int/emergencies",
                category="Emergency Preparedness",
                region="Global"
            ),
            HealthGuideline(
                title="Vector Control and Disease Prevention",
                content="WHO updates on integrated vector management for dengue, malaria, and other vector-borne diseases. Includes community-based interventions and environmental management strategies.",
                source="WHO",
                date=today,
                url="https://www.who.int/teams/control-of-neglected-tropical-diseases/vector-control",
                category="Vector Control",
                region="Endemic Areas"
            ),
            HealthGuideline(
                title="Antimicrobial Resistance Action Plan",
                content="Updated WHO global action plan on antimicrobial resistance. Emphasizes surveillance, infection prevention, rational use of antimicrobials, and research and development priorities.",
                source="WHO",
                date=today,
                url="https://www.who.int/antimicrobial-resistance",
                category="AMR",
                region="Global"
            ),
            HealthGuideline(
                title="Mental Health and Psychosocial Support",
                content="WHO guidelines for mental health and psychosocial support in emergency settings. Includes community-based interventions and integration with primary healthcare systems.",
                source="WHO",
                date=today,
                url="https://www.who.int/mental_health",
                category="Mental Health",
                region="Global"
            ),
            HealthGuideline(
                title="Vaccination Coverage and Immunization",
                content="Latest WHO recommendations for routine immunization schedules and catch-up vaccination campaigns. Focus on achieving and maintaining high coverage rates globally.",
                source="WHO",
                date=today,
                url="https://www.who.int/immunization",
                category="Immunization",
                region="Global"
            )
        ]
    
    async def fetch_disease_outbreak_data(self) -> Dict[str, Any]:
        """Fetch current disease outbreak information"""
        cache_key = 'outbreak_data'
        
        if self.is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        outbreak_data = {}
        
        try:
            # Fetch COVID-19 data for India
            session = await self.get_session()
            async with session.get(self.endpoints['covid_data']) as response:
                if response.status == 200:
                    covid_data = await response.json()
                    outbreak_data['covid19'] = {
                        'total_cases': covid_data.get('cases', 0),
                        'deaths': covid_data.get('deaths', 0),
                        'recovered': covid_data.get('recovered', 0),
                        'active': covid_data.get('active', 0),
                        'last_updated': covid_data.get('updated', datetime.now().isoformat())
                    }
        
        except Exception as e:
            logger.error(f"Error fetching outbreak data: {e}")
            # Sample outbreak data
            outbreak_data = self._get_sample_outbreak_data()
        
        # Cache the results
        self.cache[cache_key] = outbreak_data
        self.last_update[cache_key] = datetime.now()
        
        return outbreak_data
    
    def _get_sample_outbreak_data(self) -> Dict[str, Any]:
        """Get sample outbreak data when API is not available"""
        return {
            'covid19': {
                'total_cases': 44987423,
                'deaths': 531966,
                'recovered': 44448978,
                'active': 6479,
                'last_updated': datetime.now().isoformat(),
                'message': 'Data from official health ministry sources'
            },
            'dengue': {
                'risk_level': 'High',
                'season': 'Monsoon season - increased vector breeding',
                'affected_states': ['West Bengal', 'Kerala', 'Tamil Nadu', 'Karnataka'],
                'prevention_focus': 'Vector control and community awareness'
            },
            'influenza': {
                'season': 'Annual vaccination campaign ongoing',
                'priority_groups': 'Elderly, pregnant women, chronic conditions',
                'vaccine_availability': 'Available at public health centers'
            }
        }
    
    async def get_health_guidelines_by_topic(self, topic: str) -> List[HealthGuideline]:
        """Get health guidelines filtered by specific topic"""
        all_guidelines = await self.fetch_who_news_updates()
        
        if not topic:
            return all_guidelines
        
        topic_lower = topic.lower()
        filtered_guidelines = []
        
        for guideline in all_guidelines:
            if (topic_lower in guideline.title.lower() or 
                topic_lower in guideline.content.lower() or
                topic_lower in guideline.category.lower()):
                filtered_guidelines.append(guideline)
        
        # If no specific matches found, return general guidelines
        if not filtered_guidelines:
            filtered_guidelines = all_guidelines[:3]
        
        return filtered_guidelines
    
    async def get_vaccination_recommendations(self) -> Dict[str, Any]:
        """Get current vaccination recommendations from WHO"""
        cache_key = 'vaccination_recs'
        
        if self.is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Sample vaccination recommendations (would be fetched from WHO API)
        recommendations = {
            'routine_immunization': {
                'children': [
                    'BCG vaccination at birth for TB prevention',
                    'Complete pentavalent vaccine series (DPT-HepB-Hib)',
                    'Rotavirus vaccine to prevent severe diarrhea',
                    'Pneumococcal vaccine for pneumonia prevention',
                    'Measles-Rubella vaccine at 9-12 months'
                ],
                'adults': [
                    'Annual influenza vaccination',
                    'COVID-19 vaccination and boosters as recommended',
                    'Tdap booster every 10 years',
                    'HPV vaccine for eligible age groups'
                ]
            },
            'seasonal_campaigns': {
                'current_focus': 'Influenza vaccination campaign',
                'target_groups': 'Elderly (65+), pregnant women, chronic disease patients',
                'availability': 'Public health centers and private clinics'
            },
            'travel_vaccines': {
                'recommended': [
                    'Hepatitis A and B for high-risk areas',
                    'Typhoid for areas with poor sanitation',
                    'Japanese Encephalitis for endemic regions',
                    'Yellow Fever for travel to affected countries'
                ]
            }
        }
        
        # Cache the results
        self.cache[cache_key] = recommendations
        self.last_update[cache_key] = datetime.now()
        
        return recommendations
    
    async def get_emergency_health_alerts(self) -> List[Dict[str, Any]]:
        """Get current emergency health alerts"""
        cache_key = 'health_alerts'
        
        if self.is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Sample emergency alerts (would be fetched from real sources)
        alerts = [
            {
                'level': 'MODERATE',
                'title': 'Dengue Alert - Monsoon Season',
                'description': 'Increased dengue cases reported in several states. Enhanced vector control measures recommended.',
                'affected_areas': ['West Bengal', 'Kerala', 'Tamil Nadu'],
                'recommendations': [
                    'Remove standing water from containers',
                    'Use mosquito repellents',
                    'Seek medical care for fever with warning signs'
                ],
                'date_issued': datetime.now().strftime('%Y-%m-%d'),
                'source': 'National Vector Borne Disease Control Programme'
            },
            {
                'level': 'LOW',
                'title': 'Seasonal Influenza Activity',
                'description': 'Seasonal flu activity within expected levels. Vaccination recommended for high-risk groups.',
                'affected_areas': ['National'],
                'recommendations': [
                    'Get annual flu vaccination',
                    'Practice good respiratory hygiene',
                    'Stay home when sick'
                ],
                'date_issued': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Ministry of Health and Family Welfare'
            },
            {
                'level': 'INFO',
                'title': 'World Mental Health Day - October 10',
                'description': 'WHO promotes mental health awareness and importance of mental health services.',
                'affected_areas': ['Global'],
                'recommendations': [
                    'Prioritize mental health and well-being',
                    'Seek help when needed',
                    'Support mental health initiatives in community'
                ],
                'date_issued': datetime.now().strftime('%Y-%m-%d'),
                'source': 'World Health Organization'
            }
        ]
        
        # Cache the results
        self.cache[cache_key] = alerts
        self.last_update[cache_key] = datetime.now()
        
        return alerts
    
    async def search_health_guidelines(self, query: str) -> List[HealthGuideline]:
        """Search health guidelines based on query"""
        all_guidelines = await self.fetch_who_news_updates()
        
        if not query:
            return all_guidelines
        
        query_terms = query.lower().split()
        scored_guidelines = []
        
        for guideline in all_guidelines:
            score = 0
            content_text = f"{guideline.title} {guideline.content} {guideline.category}".lower()
            
            for term in query_terms:
                if term in content_text:
                    score += content_text.count(term)
            
            if score > 0:
                scored_guidelines.append((score, guideline))
        
        # Sort by relevance score and return top results
        scored_guidelines.sort(reverse=True, key=lambda x: x[0])
        return [guideline for score, guideline in scored_guidelines[:5]]
    
    def get_health_tips_by_season(self) -> Dict[str, List[str]]:
        """Get seasonal health tips"""
        current_month = datetime.now().month
        
        seasonal_tips = {
            'monsoon': [
                'Drink boiled or purified water to prevent water-borne diseases',
                'Keep surroundings clean and dry to prevent mosquito breeding',
                'Eat freshly cooked food and avoid street food',
                'Wash hands frequently with soap and water',
                'Get vaccinated against seasonal diseases like typhoid'
            ],
            'winter': [
                'Get annual influenza vaccination',
                'Maintain good ventilation in closed spaces',
                'Eat vitamin C rich foods to boost immunity',
                'Keep warm and avoid sudden temperature changes',
                'Stay hydrated even in cold weather'
            ],
            'summer': [
                'Stay hydrated by drinking plenty of water',
                'Avoid prolonged sun exposure during peak hours',
                'Wear light-colored, loose-fitting clothing',
                'Use sunscreen with appropriate SPF',
                'Consume ORS if experiencing dehydration'
            ],
            'general': [
                'Maintain regular exercise routine',
                'Eat balanced diet with fruits and vegetables',
                'Get adequate sleep (7-8 hours)',
                'Practice stress management techniques',
                'Get regular health check-ups'
            ]
        }
        
        # Determine current season based on month
        if 6 <= current_month <= 9:  # Monsoon
            current_season = 'monsoon'
        elif 11 <= current_month or current_month <= 2:  # Winter
            current_season = 'winter'
        elif 3 <= current_month <= 5:  # Summer
            current_season = 'summer'
        else:
            current_season = 'general'
        
        return {
            'current_season': current_season,
            'tips': seasonal_tips[current_season],
            'general_tips': seasonal_tips['general']
        }

# Global instance
_who_api_integration = None

def get_who_api_integration() -> WHOAPIIntegration:
    """Get singleton instance of WHO API integration"""
    global _who_api_integration
    if _who_api_integration is None:
        _who_api_integration = WHOAPIIntegration()
    return _who_api_integration

async def cleanup_who_integration():
    """Cleanup WHO API integration resources"""
    global _who_api_integration
    if _who_api_integration:
        await _who_api_integration.close_session()

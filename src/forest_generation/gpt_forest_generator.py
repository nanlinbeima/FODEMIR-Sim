"""
GPT Forest Generator

Uses GPT-4 API to generate forest specifications from natural language descriptions.
"""

import json
from typing import Dict, Any, Optional
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class GPTForestGenerator:
    """
    Generates forest specifications using GPT-4 API.
    
    Takes natural language forest descriptions and converts them to
    structured JSON format with tree species, density, and attributes.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize GPT forest generator.
        
        Args:
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            model: GPT model to use
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available. Install with: pip install openai")
        
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self.model = model
    
    def generate_forest_spec(self, prompt: str, area_m2: float = 100000,
                            target_density: float = 500) -> Dict[str, Any]:
        """
        Generate forest specification from natural language prompt.
        
        Args:
            prompt: Natural language description of forest
            area_m2: Forest area in square meters
            target_density: Target tree density (trees per hectare)
        
        Returns:
            Dictionary with forest specification
        """
        system_prompt = """You are a forestry expert specializing in forest stand structure.
Generate realistic forest specifications based on user descriptions.
Return a JSON object with the following structure:
{
  "area_m2": <area in square meters>,
  "tree_density_per_ha": <trees per hectare>,
  "species_mix": {
    "species_name": <percentage as integer>
  },
  "dbh_range_cm": {
    "min": <minimum DBH in cm>,
    "max": <maximum DBH in cm>
  },
  "height_range_m": {
    "min": <minimum height in m>,
    "max": <maximum height in m>
  },
  "description": "<brief description>"
}

Available species: pine, oak, birch, maple, spruce, beech
Ensure percentages sum to 100. Use realistic forestry values."""
        
        user_prompt = f"""Generate a forest specification with:
Area: {area_m2} m²
Target density: {target_density} trees/ha
Description: {prompt}

Return only valid JSON, no other text."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            spec = json.loads(response.choices[0].message.content)
            
            # Validate and normalize
            spec = self._validate_spec(spec, area_m2, target_density)
            
            return spec
            
        except Exception as e:
            print(f"GPT generation failed: {e}")
            # Return default specification
            return self._default_spec(area_m2, target_density)
    
    def _validate_spec(self, spec: Dict[str, Any], area_m2: float, 
                      target_density: float) -> Dict[str, Any]:
        """
        Validate and normalize generated specification.
        
        Args:
            spec: Generated specification
            area_m2: Target area
            target_density: Target density
        
        Returns:
            Validated specification
        """
        # Ensure required fields
        spec.setdefault('area_m2', area_m2)
        spec.setdefault('tree_density_per_ha', target_density)
        spec.setdefault('species_mix', {'pine': 100})
        spec.setdefault('dbh_range_cm', {'min': 15, 'max': 60})
        spec.setdefault('height_range_m', {'min': 8, 'max': 30})
        
        # Normalize species percentages
        species_mix = spec['species_mix']
        total_percent = sum(species_mix.values())
        if total_percent > 0:
            spec['species_mix'] = {sp: (pct / total_percent) * 100 
                                   for sp, pct in species_mix.items()}
        
        return spec
    
    def _default_spec(self, area_m2: float, target_density: float) -> Dict[str, Any]:
        """
        Generate default forest specification.
        
        Args:
            area_m2: Area in square meters
            target_density: Trees per hectare
        
        Returns:
            Default specification
        """
        return {
            'area_m2': area_m2,
            'tree_density_per_ha': target_density,
            'species_mix': {
                'pine': 40,
                'oak': 30,
                'birch': 20,
                'maple': 10
            },
            'dbh_range_cm': {'min': 15, 'max': 60},
            'height_range_m': {'min': 8, 'max': 30},
            'description': 'Mixed temperate forest'
        }
    
    @staticmethod
    def create_default_spec(area_m2: float = 100000, 
                           tree_density: float = 500,
                           species_mix: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Create a default forest specification without using GPT API.
        
        Args:
            area_m2: Forest area in square meters
            tree_density: Tree density in trees per hectare
            species_mix: Optional species composition dict
        
        Returns:
            Forest specification dictionary
        """
        if species_mix is None:
            species_mix = {'pine': 40, 'oak': 30, 'birch': 20, 'maple': 10}
        
        return {
            'area_m2': area_m2,
            'tree_density_per_ha': tree_density,
            'species_mix': species_mix,
            'dbh_range_cm': {'min': 15, 'max': 60},
            'height_range_m': {'min': 8, 'max': 30},
            'description': 'Generated forest specification'
        }



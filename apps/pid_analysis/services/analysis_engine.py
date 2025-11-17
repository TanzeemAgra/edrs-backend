"""
EDRS Advanced P&ID Analysis Engine
Enhanced LLM-based Oil & Gas Process Diagram Error Detection
"""

import json
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from django.conf import settings
import openai
import re
import logging

# Optional imports with graceful fallbacks
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AnalysisConfig:
    """Analysis configuration settings"""
    model: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 4000
    analysis_depth: str = "standard"  # quick, standard, deep
    include_safety_analysis: bool = True
    include_standards_check: bool = True
    confidence_threshold: float = 0.7


@dataclass
class PIDError:
    """Structured P&ID error representation"""
    category: str
    subcategory: str
    title: str
    description: str
    root_cause: str
    severity: str
    confidence: float
    element_tag: str
    line_number: str
    coordinates: Tuple[float, float]
    violated_standard: str
    standard_reference: str
    recommended_fix: str
    safety_impact: bool
    cost_impact: str


class EnhancedPIDPromptEngine:
    """Advanced P&ID Analysis Prompt System"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        
    def get_system_prompt(self, project_type: str, standard: str, analysis_depth: str) -> str:
        """Generate enhanced system prompt based on project context"""
        
        base_prompt = f"""
# EDRS - Advanced P&ID Error Detection Engine (Phase 1)

## EXPERT IDENTITY
You are a **Senior Process Engineer** with 20+ years experience in **Oil & Gas {project_type}** projects, specializing in:
- P&ID validation & design review ({standard} standards)
- Process safety management (PSM) & HAZOP studies  
- Instrumentation & control systems (ICS) design
- Piping & mechanical design standards
- Emergency shutdown systems (ESD) & safety interlocks
- Offshore/onshore facility design standards
- Engineering quality assurance & risk assessment

## ANALYSIS SCOPE & STANDARDS
**Primary Standard**: {standard}
**Project Type**: {project_type}
**Analysis Depth**: {analysis_depth}

### VALIDATION CRITERIA:
"""
        
        if standard == "isa_5_1":
            base_prompt += """
**ISA-5.1 Instrumentation Standards:**
- Tag numbering format: [Process Variable][Function][Loop Number] (e.g., FIC-001, PT-1205A)
- Symbol standardization and sizing
- Line connection conventions
- Instrument bubble conventions (shared display, computer function, etc.)
"""
        
        elif standard == "iso_10628":
            base_prompt += """
**ISO 10628 Flow Diagram Standards:**
- Equipment symbol standardization
- Piping line conventions and sizing
- Flow direction indicators
- Stream numbering systems
"""
        
        base_prompt += f"""

### ERROR CATEGORIES TO ANALYZE:

1. **SAFETY SYSTEMS** (Critical Priority)
   - PSV sizing & discharge routing to safe location
   - ESD valve locations & fail-safe positions  
   - Fire & gas detection coverage
   - Emergency venting & depressurization
   - Hazardous area classification compliance
   - Interlock logic & SIL requirements

2. **INSTRUMENTATION & CONTROL**
   - Tag numbering compliance ({standard})
   - Instrument symbol correctness
   - Control loop completeness
   - Transmitter/indicator/controller matching
   - Alarm & trip point definitions
   - Instrument air/power supply validation

3. **PIPING & MECHANICAL**
   - Line sizing & specification consistency
   - Flow direction indicators
   - Valve type selection & positioning
   - Pipe routing & support considerations
   - Thermal expansion provisions
   - Minimum pipe lengths (NPSH, etc.)

4. **PROCESS ENGINEERING**
   - Material balance consistency
   - Operating conditions compatibility  
   - Equipment sizing adequacy
   - Stream properties validation
   - Process control philosophy compliance
   - Utility requirements validation

5. **DRAFTING & STANDARDS**
   - Symbol library compliance
   - Line weights & conventions
   - Text placement & sizing
   - Drawing scale & clarity
   - Cross-reference accuracy
   - Revision control markers

## ANALYSIS METHODOLOGY:
1. **Parse** all elements systematically
2. **Cross-reference** tags, lines, and equipment
3. **Validate** against engineering standards
4. **Assess** safety & operability implications
5. **Rate** severity based on consequences
6. **Recommend** specific corrective actions

## OUTPUT FORMAT:
Return ONLY a valid JSON array of errors with this structure:
```json
[
  {{
    "category": "Safety Systems | Instrumentation | Piping | Process | Drafting",
    "subcategory": "specific area within category",
    "title": "concise error description",
    "description": "detailed technical explanation",
    "root_cause": "engineering reason for error",
    "severity": "Critical | High | Medium | Low | Info",
    "confidence": 0.95,
    "element_tag": "equipment/instrument tag if applicable",
    "line_number": "piping line number if applicable", 
    "coordinates": [x, y],
    "violated_standard": "{standard} or company standard",
    "standard_reference": "specific clause/section",
    "recommended_fix": "specific engineering action required",
    "safety_impact": true/false,
    "cost_impact": "High | Medium | Low | Minimal"
  }}
]
```

## SEVERITY CRITERIA:
- **Critical**: Safety hazard, environmental risk, code violation
- **High**: Major operability issue, equipment damage risk  
- **Medium**: Standard non-compliance, performance impact
- **Low**: Best practice improvement, maintainability
- **Info**: Optimization opportunity, suggestion

## CONSTRAINTS:
- Only analyze elements present in the provided P&ID data
- Do NOT hallucinate tags, equipment, or connections
- Mark unclear items as "Requires Verification"
- Confidence score must reflect certainty level (0.0-1.0)
- Focus on {analysis_depth} level analysis scope

## ANALYSIS SCOPE BY DEPTH:
"""
        
        if analysis_depth == "quick":
            base_prompt += "- Focus on Critical & High severity errors only\n- Safety systems priority\n- Major standards violations"
        elif analysis_depth == "standard":  
            base_prompt += "- Comprehensive error detection\n- All severity levels\n- Standards compliance check\n- Process engineering review"
        elif analysis_depth == "deep":
            base_prompt += "- Exhaustive analysis including optimization\n- Best practice recommendations\n- Detailed root cause analysis\n- Future-proofing suggestions"
            
        return base_prompt

    def get_analysis_prompt(self, pid_content: str, elements: List[str], project_context: Dict) -> str:
        """Generate analysis prompt with P&ID content"""
        
        prompt = f"""
# P&ID ANALYSIS REQUEST

## PROJECT CONTEXT:
- **Facility**: {project_context.get('facility_name', 'Not specified')}
- **Process Unit**: {project_context.get('process_unit', 'Not specified')} 
- **Operating Conditions**: {project_context.get('operating_conditions', 'Not specified')}
- **Drawing**: {project_context.get('drawing_number', 'Not specified')} Rev. {project_context.get('revision', 'A')}

## P&ID CONTENT TO ANALYZE:
{pid_content}

## DETECTED ELEMENTS:
{chr(10).join(elements) if elements else 'No elements pre-detected'}

## INSTRUCTIONS:
Perform systematic P&ID error detection analysis on the above content. 
Return results as a JSON array following the specified format.
Focus on engineering accuracy, safety compliance, and standards adherence.

Remember:
- Only report errors you can verify from the provided content
- Include specific location information where possible
- Prioritize safety-critical issues
- Provide actionable recommendations
- Use engineering judgment for severity assessment
"""
        return prompt


class PIDImageProcessor:
    """Advanced P&ID Image Processing & OCR"""
    
    def __init__(self):
        self.supported_formats = ['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'dwg']
        
    def preprocess_image(self, image_path: str) -> 'np.ndarray':
        """Enhance P&ID image for better OCR accuracy"""
        if not OPENCV_AVAILABLE:
            raise ImportError("OpenCV is required for image preprocessing. Please install opencv-python.")
        
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Enhance contrast and remove noise
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Denoise
            denoised = cv2.medianBlur(enhanced, 3)
            
            # Threshold for better text recognition
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return thresh
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise
    
    def extract_text_with_coordinates(self, image_path: str) -> List[Dict]:
        """Extract text with bounding box coordinates"""
        if not PYTESSERACT_AVAILABLE:
            raise ImportError("Pytesseract is required for text extraction. Please install pytesseract.")
        if not OPENCV_AVAILABLE:
            raise ImportError("OpenCV is required for image processing. Please install opencv-python.")
        
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)
            
            # OCR with detailed data
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-./+='
            
            data = pytesseract.image_to_data(processed_img, config=custom_config, output_type=pytesseract.Output.DICT)
            
            text_elements = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 50:  # Confidence threshold
                    text_elements.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })
            
            return text_elements
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise
    
    def extract_pid_elements(self, text_elements: List[Dict]) -> List[str]:
        """Extract P&ID specific elements from OCR text"""
        elements = []
        
        # Patterns for different P&ID elements
        patterns = {
            'instrument_tags': r'[A-Z]{1,3}[A-Z]*[-_]\d{2,4}[A-Z]?',
            'line_numbers': r'\d+"[-]\w+[-]\d+',
            'equipment_tags': r'[A-Z]{1,2}[-_]\d{2,4}[A-Z]?',
            'valve_tags': r'[A-Z]{2}V[-_]\d{2,4}',
            'pressure_ratings': r'\d+#|\d+\s*PSI|\d+\s*BAR',
            'temperatures': r'\d+°[CF]|\d+\s*DEG',
            'flow_rates': r'\d+\s*GPM|\d+\s*BPD|\d+\s*SCFH',
        }
        
        for element in text_elements:
            text = element['text'].strip()
            if len(text) < 2:
                continue
                
            for pattern_name, pattern in patterns.items():
                if re.match(pattern, text, re.IGNORECASE):
                    elements.append(f"{pattern_name.title()}: {text} (x:{element['x']}, y:{element['y']})")
        
        return elements


class AdvancedPIDAnalyzer:
    """Main P&ID Analysis Engine"""
    
    def __init__(self, config: AnalysisConfig = None):
        self.config = config or AnalysisConfig()
        self.prompt_engine = EnhancedPIDPromptEngine(self.config)
        self.image_processor = PIDImageProcessor()
        
        # Initialize OpenAI client (modern client)
        from openai import AsyncOpenAI
        self.openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=getattr(settings, 'OPENAI_TIMEOUT', 30.0),
            max_retries=getattr(settings, 'OPENAI_MAX_RETRIES', 3)
        )
    
    async def analyze_pid_diagram(
        self,
        diagram_file_path: str,
        project_context: Dict,
        progress_callback=None
    ) -> Tuple[List[PIDError], Dict]:
        """
        Complete P&ID analysis pipeline
        
        Returns:
            Tuple of (detected_errors, analysis_metadata)
        """
        start_time = time.time()
        analysis_metadata = {
            'total_processing_time': 0,
            'ocr_time': 0,
            'llm_time': 0,
            'elements_detected': 0,
            'confidence_average': 0.0,
            'model_used': self.config.model
        }
        
        try:
            if progress_callback:
                await progress_callback("Preprocessing diagram", 10)
            
            # Step 1: Image preprocessing and OCR
            ocr_start = time.time()
            text_elements = self.image_processor.extract_text_with_coordinates(diagram_file_path)
            pid_elements = self.image_processor.extract_pid_elements(text_elements)
            analysis_metadata['ocr_time'] = time.time() - ocr_start
            analysis_metadata['elements_detected'] = len(pid_elements)
            
            if progress_callback:
                await progress_callback("Extracting P&ID elements", 30)
            
            # Step 2: Prepare content for LLM analysis
            pid_content = self._format_pid_content(text_elements, pid_elements)
            
            if progress_callback:
                await progress_callback("Analyzing with AI engine", 50)
            
            # Step 3: LLM Analysis
            llm_start = time.time()
            system_prompt = self.prompt_engine.get_system_prompt(
                project_context.get('project_type', 'upstream'),
                project_context.get('standard', 'isa_5_1'),
                self.config.analysis_depth
            )
            
            analysis_prompt = self.prompt_engine.get_analysis_prompt(
                pid_content, pid_elements, project_context
            )
            
            # Call OpenAI API
            response = await self._call_openai_api(system_prompt, analysis_prompt)
            analysis_metadata['llm_time'] = time.time() - llm_start
            
            if progress_callback:
                await progress_callback("Processing results", 80)
            
            # Step 4: Parse and validate results
            detected_errors = self._parse_llm_response(response)
            analysis_metadata['confidence_average'] = self._calculate_average_confidence(detected_errors)
            
            if progress_callback:
                await progress_callback("Analysis complete", 100)
            
            analysis_metadata['total_processing_time'] = time.time() - start_time
            
            return detected_errors, analysis_metadata
            
        except Exception as e:
            logger.error(f"P&ID analysis failed: {e}")
            analysis_metadata['error'] = str(e)
            analysis_metadata['total_processing_time'] = time.time() - start_time
            raise
    
    def _format_pid_content(self, text_elements: List[Dict], pid_elements: List[str]) -> str:
        """Format extracted content for LLM analysis"""
        
        content = "## EXTRACTED P&ID TEXT ELEMENTS:\n"
        
        # Group text by spatial proximity (simple grid approach)
        spatial_groups = {}
        grid_size = 100
        
        for element in text_elements:
            if element['confidence'] > 60:
                grid_x = element['x'] // grid_size
                grid_y = element['y'] // grid_size
                key = f"{grid_x},{grid_y}"
                
                if key not in spatial_groups:
                    spatial_groups[key] = []
                spatial_groups[key].append(element['text'])
        
        # Output spatially organized content
        for position, texts in spatial_groups.items():
            content += f"\nRegion {position}: {' '.join(texts)}\n"
        
        content += "\n## IDENTIFIED P&ID ELEMENTS:\n"
        content += "\n".join(pid_elements)
        
        return content
    
    async def _call_openai_api(self, system_prompt: str, analysis_prompt: str) -> str:
        """Call OpenAI API with error handling and retries"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": analysis_prompt}
        ]
        
        try:
            # Modern OpenAI client API
            response = await self.openai_client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            # Return a fallback response for demo purposes
            return json.dumps({
                "errors": [
                    {
                        "category": "System",
                        "subcategory": "API Error",
                        "title": "Analysis Service Unavailable",
                        "description": "OpenAI API is currently unavailable. This is a demo fallback response.",
                        "severity": "Low",
                        "confidence": 0.9,
                        "recommended_fix": "Check API configuration and try again later."
                    }
                ]
            })
    
    def _parse_llm_response(self, response_text: str) -> List[PIDError]:
        """Parse and validate LLM JSON response"""
        
        try:
            # Parse JSON response
            response_data = json.loads(response_text)
            
            # Handle different response formats
            if isinstance(response_data, dict) and 'errors' in response_data:
                error_list = response_data['errors']
            elif isinstance(response_data, list):
                error_list = response_data
            else:
                raise ValueError("Unexpected response format")
            
            # Convert to PIDError objects
            detected_errors = []
            for error_data in error_list:
                try:
                    error = PIDError(
                        category=error_data.get('category', 'Unknown'),
                        subcategory=error_data.get('subcategory', ''),
                        title=error_data.get('title', 'Untitled Error'),
                        description=error_data.get('description', ''),
                        root_cause=error_data.get('root_cause', ''),
                        severity=error_data.get('severity', 'Medium'),
                        confidence=float(error_data.get('confidence', 0.5)),
                        element_tag=error_data.get('element_tag', ''),
                        line_number=error_data.get('line_number', ''),
                        coordinates=tuple(error_data.get('coordinates', [0, 0])),
                        violated_standard=error_data.get('violated_standard', ''),
                        standard_reference=error_data.get('standard_reference', ''),
                        recommended_fix=error_data.get('recommended_fix', ''),
                        safety_impact=error_data.get('safety_impact', False),
                        cost_impact=error_data.get('cost_impact', 'Low')
                    )
                    
                    # Filter by confidence threshold
                    if error.confidence >= self.config.confidence_threshold:
                        detected_errors.append(error)
                        
                except Exception as e:
                    logger.warning(f"Skipping invalid error entry: {e}")
                    continue
            
            return detected_errors
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            raise ValueError("Invalid JSON response from LLM")
    
    def _calculate_average_confidence(self, errors: List[PIDError]) -> float:
        """Calculate average confidence score"""
        if not errors:
            return 0.0
        return sum(error.confidence for error in errors) / len(errors)
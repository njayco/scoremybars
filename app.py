# =============================================================================
# ScoreMyBars - Main Flask Application
# =============================================================================
# This is the main entry point for the ScoreMyBars web application.
# It handles HTTP requests, routes, and coordinates all the components.

# Import required libraries
from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from dotenv import load_dotenv
from io import BytesIO
import base64
from datetime import datetime

# Import our custom utility classes
from utils.lyric_parser import LyricParser
from utils.ai_scorer import AIScorer
from utils.rhyme_engine import RhymeEngine

# Import export libraries
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: reportlab not available. PDF export will not work.")

try:
    from PIL import Image, ImageDraw, ImageFont
    from PIL import ImageColor
    IMAGE_AVAILABLE = True
except ImportError:
    IMAGE_AVAILABLE = False
    print("Warning: PIL not available. Image export will not work.")

# Load environment variables from .env file
# This allows us to store sensitive data like API keys outside of our code
load_dotenv()

# Create Flask application instance
app = Flask(__name__)

# Set a secret key for session management and security
# In production, this should be a strong, random key
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'scoremybars-secret-key')

# Initialize our core components
# These are the main classes that handle different aspects of lyric analysis
lyric_parser = LyricParser()  # Breaks down lyrics into sections
ai_scorer = AIScorer()        # Scores lyrics using AI or rules
rhyme_engine = RhymeEngine()  # Analyzes rhyme patterns

# =============================================================================
# ROUTES (URL endpoints that the web app responds to)
# =============================================================================

@app.route('/')
def index():
    """
    Main page route - serves the home page with the lyric input form
    This is what users see when they first visit the website
    """
    return render_template('index.html')

@app.route('/genres', methods=['GET'])
def get_genres():
    """
    API endpoint that returns available genres for comparison
    This allows users to select which genre to compare their lyrics against
    """
    try:
        genres = ai_scorer.get_available_genres()
        return jsonify({
            'success': True,
            'genres': genres
        })
    except Exception as e:
        print(f"❌ Failed to get genres: {str(e)}")
        return jsonify({'error': f'Failed to get genres: {str(e)}'}), 500

@app.route('/analyze', methods=['POST'])
def analyze_lyrics():
    """
    API endpoint that analyzes submitted lyrics and returns scores
    This is called when users click the "Analyze My Bars" button
    
    Expected input: JSON with 'lyrics' field containing the text, 'genre' field for comparison, and song metadata
    Returns: JSON with analysis results including scores and breakdowns
    """
    try:
        print("🔍 Received analyze request") # Debug log
        
        # Get the JSON data sent from the frontend
        data = request.get_json()
        print(f"📝 Received data: {data}") # Debug log
        
        lyrics = data.get('lyrics', '').strip()
        selected_genre = data.get('genre', 'hip_hop_rap')  # Default to hip-hop/rap
        song_title = data.get('song_title', '').strip()
        artist_name = data.get('artist_name', '').strip()
        
        print(f"🎵 Lyrics length: {len(lyrics)} characters") # Debug log
        print(f"🎼 Selected genre: {selected_genre}") # Debug log
        print(f"📝 Song title: {song_title}") # Debug log
        print(f"🎤 Artist name: {artist_name}") # Debug log
        
        # Validate that lyrics were provided
        if not lyrics:
            print("❌ No lyrics provided") # Debug log
            return jsonify({'error': 'No lyrics provided'}), 400
        
        # Step 1: Generate AI song description and sub-genre prediction
        print("🎯 Generating song description and sub-genre analysis...") # Debug log
        song_description = ai_scorer.generate_song_description(lyrics, song_title, artist_name, selected_genre)
        
        # Step 2: Parse lyrics into sections (verse, chorus, etc.)
        print("📝 Parsing lyrics into sections...") # Debug log
        sections = lyric_parser.parse_lyrics(lyrics)
        print(f"📊 Found {len(sections)} sections") # Debug log
        
        # Step 3: Analyze each section and collect results
        analysis_results = []
        total_scores = {
            'cleverness': 0,
            'rhyme_density': 0,
            'wordplay': 0,
            'radio_score': 0
        }
        
        # Loop through each section and analyze it
        for i, section in enumerate(sections):
            print(f"🔍 Analyzing section {i+1}: {section['type']}") # Debug log
            
            # Get AI scores for this section with genre comparison
            scores = ai_scorer.score_section(section, selected_genre)
            
            # Get rhyme analysis for this section
            rhyme_analysis = rhyme_engine.analyze_rhymes(section['text'])
            
            # Combine all the analysis data for this section
            section_result = {
                'type': section['type'],           # verse, chorus, etc.
                'text': section['text'],           # the actual lyrics
                'bar_count': section['bar_count'], # number of bars
                'scores': scores,                  # AI scores with genre comparison
                'rhyme_analysis': rhyme_analysis,  # rhyme patterns
                'highlights': ai_scorer.get_highlights(section['text'])  # standout lines
            }
            
            analysis_results.append(section_result)
            
            # Add up scores for overall average calculation
            for key in total_scores:
                total_scores[key] += scores[key]
        
        # Step 4: Calculate overall scores (average of all sections)
        num_sections = len(analysis_results)
        if num_sections > 0:
            for key in total_scores:
                total_scores[key] = round(total_scores[key] / num_sections, 1)
        
        # Step 5: Generate additional insights with genre context
        print("🎯 Generating insights...") # Debug log
        genre_prediction = ai_scorer.predict_genre(analysis_results, selected_genre)
        popularity_prediction = ai_scorer.predict_popularity(total_scores)
        suggestions = ai_scorer.generate_suggestions(total_scores, analysis_results)
        
        # Get genre information for comparison
        genre_data = ai_scorer.billboard_data.get('genres', {}).get(selected_genre, {})
        genre_name = genre_data.get('name', selected_genre.replace('_', ' ').title())
        genre_description = genre_data.get('description', '')
        
        # Step 6: Prepare the complete response
        response = {
            'success': True,
            'song_metadata': {                      # Song information
                'title': song_title,
                'artist': artist_name,
                'description': song_description
            },
            'sections': analysis_results,           # Detailed breakdown by section
            'overall_scores': total_scores,         # Overall scores
            'genre_prediction': genre_prediction,   # Predicted genre
            'popularity_prediction': popularity_prediction,  # Popularity estimate
            'suggestions': suggestions,             # Improvement suggestions
            'total_bars': sum(section['bar_count'] for section in analysis_results),  # Total bar count
            'selected_genre': {                     # Information about selected genre
                'key': selected_genre,
                'name': genre_name,
                'description': genre_description
            },
            'billboard_comparison': {               # Billboard comparison context
                'description': f'Your lyrics were compared to Billboard Hot 100 hits in the {genre_name} genre',
                'top_songs': genre_data.get('top_songs', [])[:3]  # Top 3 songs for reference
            }
        }
        
        print("✅ Analysis completed successfully") # Debug log
        return jsonify(response)
        
    except Exception as e:
        # If anything goes wrong, return an error message
        print(f"❌ Analysis failed with error: {str(e)}") # Debug log
        import traceback
        traceback.print_exc() # Print full error traceback
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/export', methods=['POST'])
def export_results():
    """
    API endpoint for exporting analysis results as PDF or image
    This allows users to save and share their results
    """
    try:
        data = request.get_json()
        export_type = data.get('type', 'pdf')  # pdf or image
        analysis_data = data.get('analysis_data', {})
        
        print(f"📤 Export request received: {export_type}")
        print(f"📊 PDF_AVAILABLE: {PDF_AVAILABLE}")
        print(f"📊 IMAGE_AVAILABLE: {IMAGE_AVAILABLE}")
        
        if export_type == 'pdf':
            if not PDF_AVAILABLE:
                print("⚠️ PDF export not available, falling back to text")
                # Fallback to text-based export
                text_content = generate_text_export(analysis_data)
                return jsonify({
                    'success': True,
                    'download_url': f"data:text/plain;base64,{base64.b64encode(text_content.encode()).decode()}",
                    'filename': f'scoremybars_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
                })
            
            try:
                # Generate PDF export
                print("📄 Generating PDF export...")
                pdf_buffer = generate_pdf_export(analysis_data)
                print("✅ PDF generated successfully")
                return jsonify({
                    'success': True,
                    'download_url': f"data:application/pdf;base64,{base64.b64encode(pdf_buffer.getvalue()).decode()}",
                    'filename': f'scoremybars_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
                })
            except Exception as e:
                print(f"❌ PDF generation failed: {e}")
                # Fallback to text-based export
                text_content = generate_text_export(analysis_data)
                return jsonify({
                    'success': True,
                    'download_url': f"data:text/plain;base64,{base64.b64encode(text_content.encode()).decode()}",
                    'filename': f'scoremybars_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
                })
                
        elif export_type == 'image':
            if not IMAGE_AVAILABLE:
                print("⚠️ Image export not available, falling back to text")
                # Fallback to text-based export
                text_content = generate_text_export(analysis_data)
                return jsonify({
                    'success': True,
                    'download_url': f"data:text/plain;base64,{base64.b64encode(text_content.encode()).decode()}",
                    'filename': f'scoremybars_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
                })
            
            try:
                # Generate image export
                print("🖼️ Generating image export...")
                image_buffer = generate_image_export(analysis_data)
                print("✅ Image generated successfully")
                return jsonify({
                    'success': True,
                    'download_url': f"data:image/png;base64,{base64.b64encode(image_buffer.getvalue()).decode()}",
                    'filename': f'scoremybars_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                })
            except Exception as e:
                print(f"❌ Image generation failed: {e}")
                # Fallback to text-based export
                text_content = generate_text_export(analysis_data)
                return jsonify({
                    'success': True,
                    'download_url': f"data:text/plain;base64,{base64.b64encode(text_content.encode()).decode()}",
                    'filename': f'scoremybars_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
                })
        else:
            return jsonify({'error': 'Invalid export type'}), 400
            
    except Exception as e:
        print(f"Export error: {e}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@app.route('/share', methods=['POST'])
def share_results():
    """
    API endpoint for sharing analysis results as an image
    This generates an image that can be shared on social media
    """
    try:
        data = request.get_json()
        analysis_data = data.get('analysis_data', {})
        
        print("📱 Share request received")
        
        if not IMAGE_AVAILABLE:
            print("⚠️ Image generation not available for sharing")
            return jsonify({'error': 'Image sharing not available'}), 400
        
        try:
            # Generate image export
            print("🖼️ Generating image for sharing...")
            image_buffer = generate_image_export(analysis_data)
            print("✅ Share image generated successfully")
            
            # Return the image data for sharing
            return jsonify({
                'success': True,
                'image_data': base64.b64encode(image_buffer.getvalue()).decode(),
                'filename': f'scoremybars_share_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            })
        except Exception as e:
            print(f"❌ Share image generation failed: {e}")
            return jsonify({'error': f'Failed to generate share image: {str(e)}'}), 500
            
    except Exception as e:
        print(f"Share error: {e}")
        return jsonify({'error': f'Share failed: {str(e)}'}), 500

def generate_text_export(analysis_data):
    """
    Generate text-based export when PDF/Image libraries are not available
    """
    lines = []
    lines.append("🎤 ScoreMyBars Analysis Report")
    lines.append("=" * 50)
    lines.append("")
    
    # Song Information
    song_metadata = analysis_data.get('song_metadata', {})
    if song_metadata:
        lines.append("📝 Song Information")
        lines.append("-" * 20)
        lines.append(f"Title: {song_metadata.get('title', 'Untitled')}")
        lines.append(f"Artist: {song_metadata.get('artist', 'Unknown Artist')}")
        
        description = song_metadata.get('description', {})
        if description:
            lines.append(f"Description: {description.get('description', 'No description available')}")
            lines.append(f"Sub-Genre: {description.get('sub_genre', 'Unknown')}")
            lines.append(f"Mood: {description.get('mood', 'Unknown')}")
            lines.append(f"Target Audience: {description.get('target_audience', 'Unknown')}")
            lines.append(f"Lyrical Style: {description.get('lyrical_style', 'Unknown')}")
            
            themes = description.get('themes', [])
            if themes:
                lines.append(f"Key Themes: {', '.join(themes)}")
        lines.append("")
    
    # Overall Scores
    overall_scores = analysis_data.get('overall_scores', {})
    if overall_scores:
        lines.append("📊 Overall Scores")
        lines.append("-" * 20)
        lines.append(f"Cleverness: {overall_scores.get('cleverness', 0)}/100")
        lines.append(f"Rhyme Density: {overall_scores.get('rhyme_density', 0)}/100")
        lines.append(f"Wordplay: {overall_scores.get('wordplay', 0)}/100")
        lines.append(f"Radio Hit: {overall_scores.get('radio_score', 0)}/100")
        lines.append("")
    
    # Section Breakdown
    sections = analysis_data.get('sections', [])
    if sections:
        lines.append("📝 Section Breakdown")
        lines.append("-" * 20)
        
        for i, section in enumerate(sections, 1):
            lines.append(f"Section {i}: {section.get('type', 'Unknown').title()}")
            lines.append(f"Bars: {section.get('bar_count', 0)}")
            
            scores = section.get('scores', {})
            if scores:
                lines.append(f"Scores - Cleverness: {scores.get('cleverness', 0)}, Rhyme: {scores.get('rhyme_density', 0)}, Wordplay: {scores.get('wordplay', 0)}, Radio: {scores.get('radio_score', 0)}")
            
            # Show first few lines of lyrics
            text = section.get('text', '')
            if text:
                lines.append("Lyrics Preview:")
                preview_lines = text.split('\n')[:3]
                for line in preview_lines:
                    lines.append(f"  {line}")
                if len(text.split('\n')) > 3:
                    lines.append("  ...")
            lines.append("")
    
    # Suggestions
    suggestions = analysis_data.get('suggestions', [])
    if suggestions:
        lines.append("💡 Improvement Suggestions")
        lines.append("-" * 20)
        for suggestion in suggestions:
            lines.append(f"• {suggestion}")
        lines.append("")
    
    # Footer
    lines.append("=" * 50)
    lines.append(f"Generated by ScoreMyBars on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    
    return '\n'.join(lines)

def generate_pdf_export(analysis_data):
    """
    Generate PDF export of analysis results using reportlab
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#ffb347')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#ffb347')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6
    )
    
    # Title
    story.append(Paragraph("🎤 ScoreMyBars Analysis Report", title_style))
    story.append(Spacer(1, 20))
    
    # Song Information
    song_metadata = analysis_data.get('song_metadata', {})
    if song_metadata:
        story.append(Paragraph("📝 Song Information", heading_style))
        story.append(Paragraph(f"<b>Title:</b> {song_metadata.get('title', 'Untitled')}", normal_style))
        story.append(Paragraph(f"<b>Artist:</b> {song_metadata.get('artist', 'Unknown Artist')}", normal_style))
        
        description = song_metadata.get('description', {})
        if description:
            story.append(Paragraph(f"<b>Description:</b> {description.get('description', 'No description available')}", normal_style))
            story.append(Paragraph(f"<b>Sub-Genre:</b> {description.get('sub_genre', 'Unknown')}", normal_style))
            story.append(Paragraph(f"<b>Mood:</b> {description.get('mood', 'Unknown')}", normal_style))
            story.append(Paragraph(f"<b>Target Audience:</b> {description.get('target_audience', 'Unknown')}", normal_style))
            story.append(Paragraph(f"<b>Lyrical Style:</b> {description.get('lyrical_style', 'Unknown')}", normal_style))
            
            themes = description.get('themes', [])
            if themes:
                story.append(Paragraph(f"<b>Key Themes:</b> {', '.join(themes)}", normal_style))
        
        story.append(Spacer(1, 20))
    
    # Overall Scores
    overall_scores = analysis_data.get('overall_scores', {})
    if overall_scores:
        story.append(Paragraph("📊 Overall Scores", heading_style))
        
        score_data = [
            ['Category', 'Score'],
            ['Cleverness', f"{overall_scores.get('cleverness', 0)}/100"],
            ['Rhyme Density', f"{overall_scores.get('rhyme_density', 0)}/100"],
            ['Wordplay', f"{overall_scores.get('wordplay', 0)}/100"],
            ['Radio Hit', f"{overall_scores.get('radio_score', 0)}/100"]
        ]
        
        score_table = Table(score_data, colWidths=[2*inch, 1*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ffb347')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.white)
        ]))
        story.append(score_table)
        story.append(Spacer(1, 20))
    
    # Section Breakdown
    sections = analysis_data.get('sections', [])
    if sections:
        story.append(Paragraph("📝 Section Breakdown", heading_style))
        
        for i, section in enumerate(sections, 1):
            story.append(Paragraph(f"<b>Section {i}: {section.get('type', 'Unknown').title()}</b>", normal_style))
            story.append(Paragraph(f"Bars: {section.get('bar_count', 0)}", normal_style))
            
            scores = section.get('scores', {})
            if scores:
                story.append(Paragraph(f"Scores - Cleverness: {scores.get('cleverness', 0)}, Rhyme: {scores.get('rhyme_density', 0)}, Wordplay: {scores.get('wordplay', 0)}, Radio: {scores.get('radio_score', 0)}", normal_style))
            
            # Show first few lines of lyrics
            text = section.get('text', '')
            if text:
                lines = text.split('\n')[:3]  # Show first 3 lines
                preview = '\n'.join(lines)
                if len(text.split('\n')) > 3:
                    preview += '\n...'
                story.append(Paragraph(f"<i>Lyrics Preview:</i><br/>{preview}", normal_style))
            
            story.append(Spacer(1, 10))
    
    # Suggestions
    suggestions = analysis_data.get('suggestions', [])
    if suggestions:
        story.append(Paragraph("💡 Improvement Suggestions", heading_style))
        for suggestion in suggestions:
            story.append(Paragraph(f"• {suggestion}", normal_style))
        story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Generated by ScoreMyBars on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_image_export(analysis_data):
    """
    Generate image export of analysis results using PIL
    """
    # Create image
    width, height = 800, 1200
    image = Image.new('RGB', (width, height), color=(44, 62, 80))  # Dark blue background
    draw = ImageDraw.Draw(image)
    
    try:
        # Try to load a font, fall back to default if not available
        font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
        font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    y_position = 30
    
    # Title
    draw.text((width//2, y_position), "🎤 ScoreMyBars Analysis Report", 
              fill=(255, 179, 71), font=font_large, anchor="mm")
    y_position += 60
    
    # Song Information
    song_metadata = analysis_data.get('song_metadata', {})
    if song_metadata:
        draw.text((30, y_position), "📝 Song Information", fill=(255, 179, 71), font=font_medium)
        y_position += 30
        
        draw.text((30, y_position), f"Title: {song_metadata.get('title', 'Untitled')}", fill=(255, 255, 255), font=font_small)
        y_position += 20
        
        draw.text((30, y_position), f"Artist: {song_metadata.get('artist', 'Unknown Artist')}", fill=(255, 255, 255), font=font_small)
        y_position += 30
        
        description = song_metadata.get('description', {})
        if description:
            draw.text((30, y_position), f"Sub-Genre: {description.get('sub_genre', 'Unknown')}", fill=(255, 255, 255), font=font_small)
            y_position += 20
            
            draw.text((30, y_position), f"Mood: {description.get('mood', 'Unknown')}", fill=(255, 255, 255), font=font_small)
            y_position += 20
            
            themes = description.get('themes', [])
            if themes:
                draw.text((30, y_position), f"Themes: {', '.join(themes)}", fill=(255, 255, 255), font=font_small)
                y_position += 30
        
        y_position += 20
    
    # Overall Scores
    overall_scores = analysis_data.get('overall_scores', {})
    if overall_scores:
        draw.text((30, y_position), "📊 Overall Scores", fill=(255, 179, 71), font=font_medium)
        y_position += 30
        
        categories = ['Cleverness', 'Rhyme Density', 'Wordplay', 'Radio Hit']
        for category in categories:
            score = overall_scores.get(category.lower().replace(' ', '_'), 0)
            draw.text((30, y_position), f"{category}: {score}/100", fill=(255, 255, 255), font=font_small)
            y_position += 20
        
        y_position += 20
    
    # Summary Stats
    total_bars = analysis_data.get('total_bars', 0)
    sections_count = len(analysis_data.get('sections', []))
    genre_prediction = analysis_data.get('genre_prediction', 'Unknown')
    
    draw.text((30, y_position), "🎯 Summary", fill=(255, 179, 71), font=font_medium)
    y_position += 30
    
    draw.text((30, y_position), f"Total Bars: {total_bars}", fill=(255, 255, 255), font=font_small)
    y_position += 20
    
    draw.text((30, y_position), f"Sections: {sections_count}", fill=(255, 255, 255), font=font_small)
    y_position += 20
    
    draw.text((30, y_position), f"Predicted Genre: {genre_prediction}", fill=(255, 255, 255), font=font_small)
    y_position += 30
    
    # Suggestions
    suggestions = analysis_data.get('suggestions', [])
    if suggestions:
        draw.text((30, y_position), "💡 Suggestions", fill=(255, 179, 71), font=font_medium)
        y_position += 30
        
        for suggestion in suggestions[:3]:  # Limit to 3 suggestions
            # Wrap text if too long
            words = suggestion.split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line + word) < 60:
                    current_line += word + " "
                else:
                    lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            
            for line in lines:
                draw.text((30, y_position), f"• {line}", fill=(255, 255, 255), font=font_small)
                y_position += 20
    
    # Footer
    y_position = height - 50
    draw.text((width//2, y_position), f"Generated on {datetime.now().strftime('%B %d, %Y')}", 
              fill=(178, 190, 195), font=font_small, anchor="mm")
    
    # Save to buffer
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

@app.route('/sample')
def get_sample_lyrics():
    """
    API endpoint that returns sample lyrics for testing
    This helps users see how the app works without writing their own lyrics
    """
    sample_lyrics = """[Verse 1]
I'm in the studio, cooking up the heat
Every bar I spit, got the crowd on their feet
Metaphors so deep, they can't compete
Wordplay so fresh, it's a lyrical treat

[Chorus]
Score my bars, let's see what you got
AI analysis, give it all you've got
From the cleverness to the radio spot
This is hip-hop, and we're taking the top

[Verse 2]
Double entendres, they don't see it coming
Punchlines so hard, got the audience humming
Internal rhymes, the flow is stunning
This is art, and I'm the one running

[Bridge]
From boom bap to trap, I can do it all
Commercial appeal, but still keeping it raw
This is the future, breaking every wall
ScoreMyBars, we're answering the call"""
    
    return jsonify({'lyrics': sample_lyrics})

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors (page not found)"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors (server errors)"""
    return render_template('500.html'), 500

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    # Check if OpenAI API key is set before starting the server
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not set. Some AI features may not work.")
        print("   Set your OpenAI API key in a .env file or environment variable.")
    
    # Get port from environment variable (for Render deployment) or use default
    port = int(os.environ.get('PORT', 5001))
    
    # Start the Flask development server
    # debug=True enables auto-reload when code changes
    # host='0.0.0.0' makes the server accessible from other devices on the network
    app.run(debug=True, host='0.0.0.0', port=port) 
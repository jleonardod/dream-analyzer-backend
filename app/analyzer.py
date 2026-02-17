import re
from collections import Counter
from typing import List, Dict, Tuple

STOP_WORDS = {
    'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no', 'haber',
    'por', 'con', 'su', 'para', 'como', 'estar', 'tener', 'le', 'lo', 'todo',
    'pero', 'más', 'hacer', 'o', 'poder', 'decir', 'este', 'ir', 'otro', 'ese',
    'la', 'si', 'me', 'ya', 'ver', 'porque', 'dar', 'cuando', 'él', 'muy',
    'sin', 'vez', 'mucho', 'saber', 'qué', 'sobre', 'mi', 'alguno', 'mismo',
    'yo', 'también', 'hasta', 'año', 'dos', 'querer', 'entre', 'así', 'primero',
    'desde', 'grande', 'eso', 'ni', 'nos', 'llegar', 'pasar', 'tiempo', 'ella',
    'sí', 'día', 'uno', 'bien', 'poco', 'deber', 'entonces', 'poner', 'cosa',
    'tanto', 'hombre', 'parecer', 'nuestro', 'tan', 'donde', 'ahora', 'parte',
    'después', 'vida', 'quedar', 'siempre', 'creer', 'hablar', 'llevar', 'dejar',
    'nada', 'cada', 'seguir', 'menos', 'nuevo', 'encontrar', 'algo', 'solo',
    'decir', 'casa', 'usar', 'uno', 'tal', 'otro', 'esta', 'estos', 'estas',
    'esos', 'esas', 'aquel', 'aquella', 'aquellos', 'aquellas', 'fue', 'era',
    'estaba', 'había', 'ante', 'bajo', 'contra', 'desde', 'durante', 'mediante',
    'hacia', 'según', 'tras', 'son', 'fue', 'han', 'todo', 'toda', 'todos', 'todas',
    'les', 'has', 'estoy', 'estás', 'está', 'estamos', 'están'
}

EMOTION_WORDS = {
    'feliz': ['feliz', 'alegre', 'contento', 'felicidad', 'alegría', 'gozo', 'dicha', 
              'encantado', 'emocionado', 'eufórico', 'radiante', 'sonriente'],
    'triste': ['triste', 'tristeza', 'melancolía', 'deprimido', 'afligido', 'apenado', 
               'desolado', 'desconsolado', 'melancólico', 'llorar', 'lágrimas'],
    'miedo': ['miedo', 'terror', 'pánico', 'asustado', 'aterrado', 'espanto', 'horror',
              'temor', 'angustia', 'ansiedad', 'nervioso', 'preocupado', 'amenaza'],
    'enojo': ['enojo', 'ira', 'rabia', 'furia', 'enojado', 'furioso', 'irritado', 
              'molesto', 'enfadado', 'indignado', 'frustrado'],
    'amor': ['amor', 'cariño', 'afecto', 'ternura', 'amar', 'querer', 'adorar',
             'apreciar', 'amado', 'querido', 'romántico', 'pasión'],
    'sorpresa': ['sorpresa', 'sorprendido', 'asombrado', 'impresionado', 'atónito',
                 'maravillado', 'inesperado', 'increíble', 'asombroso'],
    'calma': ['calma', 'paz', 'tranquilo', 'sereno', 'relajado', 'pacífico', 
              'sosegado', 'plácido', 'tranquilidad', 'serenidad']
}

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\sáéíóúñü]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_words(text: str) -> List[str]:
    clean = clean_text(text)
    words = clean.split()
    filtered = [w for w in words if len(w) > 3 and w not in STOP_WORDS]
    return filtered

def get_word_frequency(texts: List[str], top_n: int  = 20) -> List[Dict]:
    all_words = []
    for text in texts:
        all_words.extend(extract_words(text))

    if not all_words:
        return []
    
    word_counts = Counter(all_words)
    total_words = len(all_words)

    most_common = word_counts.most_common(top_n)

    return [
        {
            'word': word,
            'count': count,
            'percentage': round((count / total_words) * 100, 2)
        }
        for word, count in most_common
    ]

def detect_emotion(text: str) -> Tuple[str, float]:
    clean = clean_text(text)
    words = set(clean.split())

    emotion_scores = {}

    for emotion, keywords in EMOTION_WORDS.items():
        matches = sum(1 for keyword in keywords if keyword in clean)
        if matches > 0:
            emotion_scores[emotion] = matches

    if not emotion_scores:
        return None, 0.0
    
    dominant_emotion = max(emotion_scores, key = emotion_scores.get)
    max_score = emotion_scores[dominant_emotion]

    normalized_score = min(1.0, max_score / 5.0)

    return dominant_emotion, round(normalized_score, 2)

def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    words = extract_words(text)

    if not words:
        return []
    
    word_counts = Counter(words)
    keywords = [word for word, _ in word_counts.most_common(top_n)]

    return keywords

def suggest_tags(text: str) -> List[str]:

    categories = {
        'familia': ['madre', 'padre', 'mamá', 'papá', 'hermano', 'hermana', 'hijo', 
                    'hija', 'abuelo', 'abuela', 'primo', 'tío', 'familia'],
        'trabajo': ['trabajo', 'oficina', 'jefe', 'compañero', 'proyecto', 'reunión',
                    'empresa', 'negocio', 'carrera'],
        'amor': ['pareja', 'novio', 'novia', 'esposo', 'esposa', 'beso', 'abrazo',
                 'cita', 'romántico', 'amor'],
        'viaje': ['viaje', 'avión', 'aeropuerto', 'hotel', 'vacaciones', 'playa',
                  'montaña', 'ciudad', 'camino', 'destino'],
        'casa': ['casa', 'hogar', 'habitación', 'cocina', 'baño', 'sala', 'jardín'],
        'animales': ['perro', 'gato', 'pájaro', 'animal', 'mascota', 'caballo', 
                     'serpiente', 'pez'],
        'naturaleza': ['árbol', 'bosque', 'río', 'lago', 'mar', 'montaña', 'cielo',
                       'lluvia', 'sol', 'luna', 'estrella', 'flor'],
        'persecución': ['perseguir', 'correr', 'escapar', 'huir', 'persecución',
                        'chase', 'seguir'],
        'caída': ['caer', 'caída', 'precipicio', 'altura', 'volar'],
        'agua': ['agua', 'nadar', 'río', 'mar', 'océano', 'piscina', 'lluvia', 'ahogarse'],
        'muerte': ['muerte', 'morir', 'muerto', 'funeral', 'cementerio'],
        'escuela': ['escuela', 'colegio', 'universidad', 'clase', 'examen', 'profesor',
                    'estudiante', 'tarea'],
        'comida': ['comida', 'comer', 'restaurante', 'cocinar', 'hambre', 'alimento']
    }
    
    clean = clean_text(text)
    suggested = []

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in clean:
                suggested.append(category)
                break
    
    return suggested

def analyze_dream_text(text: str) -> Dict:
    keywords = extract_keywords(text, top_n=10)
    emotion, emotion_score = detect_emotion(text)
    tags = suggest_tags(text)
    word_count = len(extract_words(text))

    return {
        'keywords': keywords,
        'word_count': word_count,
        'emotion': emotion,
        'emotion_score': emotion_score,
        'suggested_tags': tags
    }

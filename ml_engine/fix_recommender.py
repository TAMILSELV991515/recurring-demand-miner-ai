import numpy as np
from datetime import datetime
from collections import Counter
from .preprocessor import clean_text
from .vectorizer import TextVectorizer, compute_cosine_similarity
from .clusterer import KMeansClusterer, DBSCANClusterer, extract_cluster_name

RECOMMENDED_FIX_TEMPLATES = {
    'Hardware': "Deploy updated device drivers, configure hardware auto-health monitoring, and initiate proactive battery/hardware replacement for flagged asset serial numbers.",
    'Application': "Apply database index optimization, deploy bug patch v4.2, increase request connection timeout, and establish automated retry/archive background routines.",
    'Access': "Reconfigure SAML SSO token refresh lifetime parameters, enable self-service password/MFA portal, and automate employee role-based access provisioning.",
    'Network': "Upgrade RADIUS/VPN gateway firmware, optimize access point load balancing, and implement redundant failover network routes.",
    'Server': "Optimize VM resource allocation templates, automate disk space purge scripts, and configure container auto-scaling triggers.",
    'Facilities': "Upgrade badge reader firmware and integrate HR onboarding system with physical access control system."
}

def analyze_and_rank_clusters(tickets, algorithm='KMeans', n_clusters=8, eps=0.4):
    """
    Runs text vectorization, clustering, metrics calculation, and permanent fix recommendation.
    Returns ranked list of cluster summaries.
    """
    if not tickets:
        return []
    
    cleaned_texts = [clean_text(t['short_description']) for t in tickets]
    vectorizer = TextVectorizer(max_features=1000)
    matrix = vectorizer.fit_transform(cleaned_texts)
    
    if matrix.shape[0] == 0:
        return []
    
    if algorithm == 'DBSCAN':
        clusterer = DBSCANClusterer(eps=eps, min_samples=3)
        labels = clusterer.fit_predict(matrix)
    else:
        clusterer = KMeansClusterer(n_clusters=n_clusters)
        labels = clusterer.fit_predict(matrix)
        
    sim_matrix = compute_cosine_similarity(matrix)
    
    # Group tickets by assigned cluster label
    clusters_map = {}
    for idx, label in enumerate(labels):
        if label == -1: # Ignore unclustered noise in DBSCAN
            continue
        if label not in clusters_map:
            clusters_map[label] = []
        clusters_map[label].append(idx)
        
    results = []
    
    for label, indices in clusters_map.items():
        if len(indices) < 2: # Exclude tiny single-ticket noise clusters
            continue
            
        cluster_tickets = [tickets[i] for i in indices]
        cluster_texts = [cleaned_texts[i] for i in indices]
        
        # Calculate cluster properties
        category = Counter([t['category'] for t in cluster_tickets]).most_common(1)[0][0]
        issue_name = extract_cluster_name(cluster_texts, feature_names=vectorizer.feature_names)
        
        ticket_count = len(cluster_tickets)
        total_effort = sum(t['effort_hours'] for t in cluster_tickets)
        avg_res_time = total_effort / ticket_count if ticket_count > 0 else 1.0
        
        workaround_count = sum(1 for t in cluster_tickets if t['is_workaround'] == 1)
        workaround_pct = round((workaround_count / ticket_count) * 100, 1)
        
        affected_assets = list(set([t['affected_asset'] for t in cluster_tickets if t['affected_asset'] != 'N/A']))
        affected_assets_str = ", ".join(affected_assets[:4]) if affected_assets else "Fleet / Multiple"
        
        # Calculate Recurrence Interval (average delta days between consecutive created dates)
        dates = []
        for t in cluster_tickets:
            try:
                dt = datetime.strptime(t['created_date'], '%Y-%m-%d %H:%M')
                dates.append(dt)
            except Exception:
                pass
        dates.sort()
        
        if len(dates) > 1:
            deltas = [(dates[i] - dates[i-1]).total_seconds() / 86400.0 for i in range(1, len(dates))]
            avg_recurrence_days = round(np.mean(deltas), 1)
        else:
            avg_recurrence_days = 3.5
            
        if avg_recurrence_days <= 0:
            avg_recurrence_days = 0.5
            
        # Confidence score based on internal cosine similarity matrix
        sub_sim = sim_matrix[np.ix_(indices, indices)]
        confidence_score = round(float(np.mean(sub_sim)) * 100, 1)
        
        # Business Impact assessment
        if ticket_count >= 15 or total_effort >= 20:
            business_impact = "CRITICAL - High Support Consumption"
            impact_weight = 30
        elif ticket_count >= 8 or total_effort >= 10:
            business_impact = "HIGH - Moderate Operational Friction"
            impact_weight = 20
        else:
            business_impact = "MEDIUM - Recurring End-User Nuisance"
            impact_weight = 10
            
        # Recommendation & ROI Metrics
        recommended_fix = RECOMMENDED_FIX_TEMPLATES.get(category, RECOMMENDED_FIX_TEMPLATES['Application'])
        
        # Formula for priority score
        priority_score = round((ticket_count * 0.4) + (workaround_pct * 0.3) + (total_effort * 0.3) + impact_weight, 1)
        
        expected_reduction_pct = 85.0 if workaround_pct > 50 else 75.0
        time_saved_hrs = round((total_effort * (expected_reduction_pct / 100.0)), 1)
        cost_saved_usd = round(time_saved_hrs * 50.0, 2) # Standard IT engineer rate $50/hr
        
        cluster_id_str = f"CL-{category.upper()[:3]}-{label+1:02d}"
        
        results.append({
            'cluster_id': cluster_id_str,
            'cluster_name': f"{category}: {issue_name}",
            'issue_description': cluster_tickets[0]['short_description'],
            'category': category,
            'ticket_count': ticket_count,
            'avg_resolution_time_hrs': round(avg_res_time, 2),
            'total_effort_hours': round(total_effort, 2),
            'workaround_freq_pct': workaround_pct,
            'affected_assets': affected_assets_str,
            'recurrence_interval_days': avg_recurrence_days,
            'estimated_business_impact': business_impact,
            'confidence_score': min(99.5, max(65.0, confidence_score)),
            'recommended_fix': recommended_fix,
            'priority_score': priority_score,
            'expected_ticket_reduction_pct': expected_reduction_pct,
            'time_saved_hours': time_saved_hrs,
            'cost_saved_usd': cost_saved_usd,
            'algorithm_used': algorithm
        })
        
    # Sort descending by priority score
    results.sort(key=lambda x: x['priority_score'], reverse=True)
    return results

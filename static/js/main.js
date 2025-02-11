document.addEventListener('DOMContentLoaded', function() {
    console.log('Script chargé');

    // Sélection des éléments du DOM
    const channelInput = document.getElementById('channel-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultsContainer = document.getElementById('results');
    const loadingOverlay = document.getElementById('loading');

    console.log('Éléments trouvés:', {
        input: channelInput !== null,
        button: analyzeBtn !== null,
        results: resultsContainer !== null,
        loading: loadingOverlay !== null
    });

    // Vérifier que les éléments existent
    if (!channelInput || !analyzeBtn || !resultsContainer || !loadingOverlay) {
        console.error('Certains éléments du DOM sont manquants');
        return;
    }

    // Fonction pour afficher le chargement
    function showLoading() {
        loadingOverlay.style.display = 'flex';
    }

    // Fonction pour cacher le chargement
    function hideLoading() {
        loadingOverlay.style.display = 'none';
    }

    // Fonction pour afficher une erreur
    function showError(message) {
        resultsContainer.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <p>${message}</p>
            </div>
        `;
        hideLoading();
    }

    // Fonction pour analyser la chaîne
    async function analyzeChannel(channelUrl) {
        console.log('Analyse de la chaîne:', channelUrl);
        
        if (!channelUrl) {
            showError('Veuillez entrer une URL de chaîne YouTube');
            return;
        }

        try {
            showLoading();
            
            // Encoder l'URL pour la requête GET
            const encodedUrl = encodeURIComponent(channelUrl);
            const response = await fetch(`/api/analyze-channel?channel_url=${encodedUrl}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erreur lors de l\'analyse de la chaîne');
            }

            const data = await response.json();
            hideLoading();
            displayResults(data);
        } catch (error) {
            console.error('Erreur:', error);
            showError(error.message);
        }
    }

    // Fonction pour afficher les résultats
    function displayResults(data) {
        const formatNumber = (num) => num?.toLocaleString() || '0';
        const calculateEngagementRate = (likes, views) => ((likes / views) * 100).toFixed(2);

        const html = `
            <div class="results-container">
                <!-- Vue d'ensemble de la chaîne -->
                <div class="channel-card">
                    <div class="channel-header">
                        <h2 class="channel-title">${data.channel_info?.title || 'Chaîne YouTube'}</h2>
                    </div>
                    <div class="channel-stats">
                        <div class="stat-box">
                            <div class="stat-value">${formatNumber(data.channel_info?.subscriber_count)}</div>
                            <div class="stat-label">Abonnés</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">${formatNumber(data.channel_info?.video_count)}</div>
                            <div class="stat-label">Vidéos</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">${formatNumber(data.channel_info?.view_count)}</div>
                            <div class="stat-label">Vues totales</div>
                        </div>
                    </div>
                </div>

                <!-- Métriques de performance -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3><i class="fas fa-chart-line"></i> Performance Moyenne</h3>
                        <div class="metric-content">
                            <div class="metric-item">
                                <div class="metric-item-value">${formatNumber(data.analysis?.performance_metrics?.average_views)}</div>
                                <div class="metric-item-label">Vues</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-item-value">${formatNumber(data.analysis?.performance_metrics?.average_likes)}</div>
                                <div class="metric-item-label">Likes</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-item-value">${formatNumber(data.analysis?.performance_metrics?.average_comments)}</div>
                                <div class="metric-item-label">Commentaires</div>
                            </div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <h3><i class="fas fa-clock"></i> Timing Optimal</h3>
                        <div class="metric-content">
                            <div class="metric-item">
                            <div class="metric-item-value">${data.analysis?.temporal_patterns?.best_days || 'N/A'}</div>
                            <div class="metric-item-label">Meilleur jour</div>
                            </div>
                            <div class="metric-item">
                            <div class="metric-item-value">${data.analysis?.temporal_patterns?.best_hours || 'N/A'}h</div>
                            <div class="metric-item-label">Meilleure heure</div>
                            </div>
                            <div class="metric-item">
                            <div class="metric-item-value">${data.analysis?.temporal_patterns?.posting_frequency || 'N/A'}</div>
                            <div class="metric-item-label">Fréquence</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Meilleures vidéos -->
                <div class="videos-section">
                    <h3><i class="fas fa-trophy"></i> Vidéos les Plus Performantes</h3>
                    <div class="videos-grid">
                        ${data.analysis?.performance_metrics?.top_performing_videos?.map((video, index) => `
                            <div class="video-card">
                                <span class="video-rank">#${index + 1}</span>
                                <h4 class="video-title">${video.title}</h4>
                                <div class="video-metrics">
                                    <div class="video-metric">
                                        <div class="video-metric-value">${formatNumber(video.view_count)}</div>
                                        <div class="video-metric-label">Vues</div>
                                    </div>
                                    <div class="video-metric">
                                        <div class="video-metric-value">${formatNumber(video.like_count)}</div>
                                        <div class="video-metric-label">Likes</div>
                                    </div>
                                    <div class="video-metric">
                                        <div class="video-metric-value">${calculateEngagementRate(video.like_count, video.view_count)}%</div>
                                        <div class="video-metric-label">Engagement</div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- Mots-clés -->
                <div class="keywords-section">
                    <h3><i class="fas fa-tags"></i> Mots-clés Populaires</h3>
                    <div class="keywords-cloud">
                        ${data.analysis?.content_patterns?.common_keywords?.map(keyword => 
                            `<span class="keyword-tag">${keyword}</span>`
                        ).join('')}
                    </div>
                </div>

                <!-- Suggestions de l'IA -->
                <div class="ai-suggestions-section">
                    <h3><i class="fas fa-lightbulb"></i> Suggestions de Vidéos</h3>
                    <div class="suggestions-grid">
                        ${data.ai_suggestions?.map((suggestion, index) => `
                            <div class="suggestion-card">
                                <div class="suggestion-header">
                                    <span class="suggestion-number">#${index + 1}</span>
                                    <div class="suggestion-potential">
                                        <i class="fas fa-chart-line"></i>
                                        ${suggestion.estimated_potential}
                                    </div>
                                </div>
                                <h4 class="suggestion-title">${suggestion.title}</h4>
                                <p class="suggestion-description">${suggestion.description}</p>
                                <div class="suggestion-topic">
                                    <i class="fas fa-bullseye"></i>
                                    ${suggestion.topic}
                                </div>
                                <div class="suggestion-key-points">
                                    <h5><i class="fas fa-check-circle"></i> Points Clés:</h5>
                                    <ul>
                                        ${suggestion.key_points.map(point => 
                                            `<li>${point}</li>`
                                        ).join('')}
                                    </ul>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;


        resultsContainer.innerHTML = html;
    }

    // Activer/désactiver le bouton en fonction de l'input
    function updateButtonState() {
        const channelUrl = channelInput.value.trim();
        const isDisabled = channelUrl.length === 0;
        
        analyzeBtn.disabled = isDisabled;
        if (isDisabled) {
            analyzeBtn.classList.add('disabled');
        } else {
            analyzeBtn.classList.remove('disabled');
        }
        
        console.log('État du bouton mis à jour:', {
            url: channelUrl,
            disabled: isDisabled
        });
    }

    // Gestionnaire d'événement pour l'input
    channelInput.addEventListener('input', updateButtonState);
    channelInput.addEventListener('keypress', function(e) {
        console.log('Touche pressée:', e.key);
        if (e.key === 'Enter' && !analyzeBtn.disabled) {
            e.preventDefault();
            analyzeChannel(this.value.trim());
        }
    });

    // Gestionnaire d'événement pour le bouton
    analyzeBtn.addEventListener('click', function() {
        console.log('Bouton cliqué');
        const channelUrl = channelInput.value.trim();
        if (channelUrl) {
            analyzeChannel(channelUrl);
        }
    });

    // Initialiser l'état du bouton
    updateButtonState();

    // Focus sur l'input au chargement
    channelInput.focus();
    
    console.log('Initialisation terminée');
});
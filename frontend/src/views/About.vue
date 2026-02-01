<template>
  <div class="min-h-screen bg-slate-950 relative overflow-hidden flex flex-col">
    <!-- Background Effects -->
    <div class="absolute inset-0 opacity-20 pointer-events-none">
      <div class="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_0%,rgba(6,182,212,0.15),transparent_70%)]"></div>
      <div class="absolute bottom-0 right-0 w-96 h-96 bg-purple-500 rounded-full mix-blend-screen filter blur-[128px]"></div>
      <div class="absolute top-1/2 left-0 w-96 h-96 bg-cyan-500 rounded-full mix-blend-screen filter blur-[128px]"></div>
    </div>

    <!-- Header -->
    <div class="relative z-10 px-6 pt-12 pb-8 text-center max-w-4xl mx-auto">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-bold uppercase tracking-widest mb-6 animate-fade-in-down">
        <span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
        Next Gen Launcher
      </div>
      
      <h1 class="text-5xl md:text-7xl font-bold bg-gradient-to-br from-white via-cyan-100 to-slate-400 bg-clip-text text-transparent mb-6 drop-shadow-lg tracking-tight">
        O Futuro dos Downloads
      </h1>
      
      <p class="text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
        Uma experiência simplificada, gratuita e desenhada para performance. 
        Gerencie sua biblioteca de conteúdos com a velocidade que você merece.
      </p>
    </div>

    <!-- Feature Grid -->
    <div class="relative z-10 flex-1 px-4 md:px-8 pb-12">
      <div class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        <!-- Feature 1: Velocidade -->
        <div class="group relative p-8 bg-slate-900/50 backdrop-blur-xl border border-white/5 hover:border-cyan-500/30 rounded-3xl transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-500/10 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="relative z-10">
            <div class="w-14 h-14 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-cyan-500/20 group-hover:scale-110 transition-transform">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 class="text-2xl font-bold text-white mb-3">Ultra High Speed</h3>
            <p class="text-slate-400 leading-relaxed">
              Downloads otimizados via multi-thread que alcançam velocidades <strong class="text-cyan-400">3x a 4x maiores</strong> que os launchers tradicionais. Extraia o máximo da sua banda larga.
            </p>
          </div>
        </div>

        <!-- Feature 2: Fontes JSON -->
        <div class="group relative p-8 bg-slate-900/50 backdrop-blur-xl border border-white/5 hover:border-amber-500/30 rounded-3xl transition-all duration-300 hover:shadow-2xl hover:shadow-amber-500/10 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="relative z-10">
            <div class="w-14 h-14 bg-gradient-to-br from-amber-500 to-orange-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-amber-500/20 group-hover:scale-110 transition-transform">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
            </div>
            <h3 class="text-2xl font-bold text-white mb-3">Fontes Descentralizadas</h3>
            <p class="text-slate-400 leading-relaxed">
              Adicione suas próprias fontes JSON. Um ecossistema aberto onde você controla de onde vêm seus downloads, sem depender de uma loja centralizada.
            </p>
          </div>
        </div>

        <!-- Feature 3: Smart Library -->
        <div class="group relative p-8 bg-slate-900/50 backdrop-blur-xl border border-white/5 hover:border-purple-500/30 rounded-3xl transition-all duration-300 hover:shadow-2xl hover:shadow-purple-500/10 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="relative z-10">
            <div class="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-purple-500/20 group-hover:scale-110 transition-transform">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3 class="text-2xl font-bold text-white mb-3">Biblioteca Inteligente</h3>
            <p class="text-slate-400 leading-relaxed">
              Catalogação automática com metadados ricos: capas, trailers, sinopses e requisitos. Sua coleção de arquivos organizada automaticamente e bonita de se ver.
            </p>
          </div>
        </div>

        <!-- Feature 4: Tecnologias Modernas -->
        <div class="group relative p-8 bg-slate-900/50 backdrop-blur-xl border border-white/5 hover:border-emerald-500/30 rounded-3xl transition-all duration-300 hover:shadow-2xl hover:shadow-emerald-500/10 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="relative z-10">
            <div class="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-emerald-500/20 group-hover:scale-110 transition-transform">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-2xl font-bold text-white mb-3">Stack Robusta</h3>
            <p class="text-slate-400 leading-relaxed">
              Construído sobre <strong class="text-emerald-400">Vue 3</strong> e <strong class="text-emerald-400">Electron</strong>, garantindo uma interface fluida, responsiva e compatível com as tecnologias web mais recentes.
            </p>
          </div>
        </div>

        <!-- Feature 5: Tradução Global -->
        <div class="group relative p-8 bg-slate-900/50 backdrop-blur-xl border border-white/5 hover:border-blue-400/30 rounded-3xl transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-blue-400/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="relative z-10">
            <div class="w-14 h-14 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-blue-400/20 group-hover:scale-110 transition-transform">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
              </svg>
            </div>
            <h3 class="text-2xl font-bold text-white mb-3">Tradução Nativa</h3>
            <p class="text-slate-400 leading-relaxed">
              Sistema de tradução "Dual-Fetch" que detecta o idioma do seu Windows e adapta todo o conteúdo, mantendo as imagens e vídeos originais intactos.
            </p>
          </div>
        </div>

        <!-- Feature 6: Privacidade e Segurança -->
        <div class="group relative p-8 bg-slate-900/50 backdrop-blur-xl border border-white/5 hover:border-green-500/30 rounded-3xl transition-all duration-300 hover:shadow-2xl hover:shadow-green-500/10 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-green-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="relative z-10">
            <div class="w-14 h-14 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-green-500/20 group-hover:scale-110 transition-transform">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 class="text-2xl font-bold text-white mb-3">100% Local & Seguro</h3>
            <p class="text-slate-400 leading-relaxed">
              Aplicação leve e independente. Não coletamos dados, não usamos servidores externos. A relação é unicamente entre você e o app. Entregamos a funcionalidade, você controla o uso.
            </p>
          </div>
        </div>

      </div>
    </div>

    <!-- Legal Disclaimer -->
    <div class="px-6 pb-8 relative z-10">
      <div class="max-w-4xl mx-auto p-6 bg-red-900/10 border border-red-500/20 rounded-2xl backdrop-blur-sm">
        <h4 class="text-red-400 font-bold mb-2 flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Aviso de Responsabilidade
        </h4>
        <p class="text-slate-400 text-sm leading-relaxed text-justify">
          Esta aplicação é uma ferramenta limpa de gerenciamento e não hospeda nenhum conteúdo.
          <strong>Não nos responsabilizamos pelos conteúdos baixados.</strong> A segurança e integridade dos arquivos (incluindo riscos de malware) são de total responsabilidade do usuário e da fonte de onde o conteúdo é obtido. 
          Use fontes confiáveis.
        </p>
      </div>
    </div>

    <!-- Back Button Area -->
    <div class="p-8 text-center relative z-10 border-t border-white/5 bg-slate-950/50 backdrop-blur-sm">
      <router-link to="/">
        <button class="px-8 py-3 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-xl border border-slate-700 hover:border-cyan-500/50 transition-all shadow-lg hover:shadow-cyan-500/20 flex items-center gap-2 mx-auto">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Voltar ao Dashboard
        </button>
      </router-link>
      <p class="mt-4 text-xs text-slate-600 font-mono">v3.3.1 • Dev: FuriousOfNightGames</p>
    </div>
  </div>
</template>

<script setup>
// Component logic maps to static presentation
</script>

<style scoped>
/* Animação suave de entrada */
@keyframes fade-in-down {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in-down {
  animation: fade-in-down 0.8s ease-out;
}
</style>

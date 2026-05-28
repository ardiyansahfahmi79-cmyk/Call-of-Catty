import streamlit as st
import random

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="🐱 PERANG KERAJAAN KUCING | MEOWSTAR vs CAKAR BESI",
    page_icon="🐱‍🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= CSS KHUSUS untuk nuansa perang =================
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 20% 30%, #0a0f1e, #010101);
    }
    .reportview-container .main .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    h1, h2, h3 {
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 5px #ff5500;
    }
    .stButton > button {
        background: #2c2118;
        border: 2px solid #e67e22;
        color: #ffd966;
        font-weight: bold;
        border-radius: 30px;
        transition: 0.1s;
    }
    .stButton > button:hover {
        background: #e67e22;
        color: black;
        transform: scale(1.02);
    }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================= GAME HTML (Embed dengan tinggi penuh) =================
GAME_HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>🐱 PERANG TOTAL: MEOWSTAR vs CAKAR BESI 🐱</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; user-select: none; }
        body { background: #000; display: flex; justify-content: center; align-items: center; min-height: 100vh; font-family: 'Courier New', monospace; }
        #gameWrapper { display: flex; flex-direction: column; align-items: center; gap: 8px; width: 100%; max-width: 1200px; }
        canvas { border-radius: 20px; box-shadow: 0 20px 35px black, 0 0 0 3px #ffb347; cursor: crosshair; width: 100%; height: auto; background: black; }
        .war-panel { display: flex; gap: 15px; background: #0b0e1acc; backdrop-filter: blur(12px); padding: 8px 20px; border-radius: 50px; color: #ffefc0; font-weight: bold; align-items: center; justify-content: space-between; width: 100%; flex-wrap: wrap; }
        .action-buttons { display: flex; gap: 12px; }
        .war-button { background: #2c2118; border: 2px solid #e67e22; color: #ffd966; font-family: monospace; font-weight: bold; padding: 6px 18px; border-radius: 40px; cursor: pointer; transition: 0.05s linear; }
        .war-button:active { transform: scale(0.95); background: #e67e22; color: black; }
        .stats { display: flex; gap: 24px; background: #000000aa; padding: 5px 18px; border-radius: 30px; }
        #warDialog { background: #000000bb; padding: 6px 16px; border-radius: 28px; font-size: 14px; max-width: 400px; white-space: nowrap; overflow-x: auto; }
        @media (max-width: 700px) { .stats { font-size: 12px; gap: 12px; } .war-button { padding: 3px 10px; font-size: 12px; } }
    </style>
</head>
<body>
<div id="gameWrapper">
    <canvas id="warCanvas" width="1000" height="600" style="width:100%; height:auto; max-width:1000px; aspect-ratio:1000/600"></canvas>
    <div class="war-panel">
        <div class="action-buttons">
            <button class="war-button" id="reloadBtn">🔁 RELOAD (R)</button>
            <button class="war-button" id="sprintBtn">🏃 SPRINT (Shift)</button>
        </div>
        <div class="stats">
            <span>❤️ <span id="hpStat">0</span></span>
            <span>🐟 <span id="ammoStat">0</span></span>
            <span>⭐ <span id="scoreStat">0</span></span>
        </div>
        <div id="warDialog">⚡ PERANG DIMULAI! Klik kanan gerak | Klik kiri tembak | Spasi lanjut cerita</div>
    </div>
</div>

<script>
    (function(){
        const canvas = document.getElementById('warCanvas');
        const ctx = canvas.getContext('2d');
        
        // =============== CERITA PANJANG (EPIC DRAMA) ===============
        let gamePhase = 'story';
        let storyQueue = [];
        const WAR_STORY = [
            { speaker: "🇫🇲 JENDERAL KUMIS EMAS", avatar: "🐱‍👑", text: "Federasi Meowstar diserang tanpa peringatan! Kerajaan Cakar Besi melintasi batas dengan 300 tank!" },
            { speaker: "🇮🇷 KOMANDAN BAJINGAN", avatar: "😾⚙️", text: "Hahaha! Tanah kalian akan menjadi padang pasir! Artileri kami akan menghujani kota!" },
            { speaker: "🇫🇲 LETNAN BULU PERAK", avatar: "🐱‍✈️", text: "Jenderal! Mereka membantai warga sipil! Jalanan dipenuhi kawah dan jejak tank!" },
            { speaker: "🇫🇲 JENDERAL", avatar: "🐱‍👑", text: "Aktifkan semua kucing tentara! Jangan biarkan satu pun musuh hidup!" },
            { speaker: "🇫🇲 SERGEANT COMBAT", avatar: "🐱‍🔫", text: "Kami sudah siap, Pak! Rudal ikan terisi penuh!" },
            { speaker: "🇮🇷 TANK COMMANDER", avatar: "💀😾", text: "Tak ada yang bisa hentikan kendaraan lapis baja kami!" },
            { speaker: "🇫🇲 JENDERAL", avatar: "🐱‍👑", text: "Untuk Meowstar! SERBU! Tembak tepat di celah baju besi mereka!" }
        ];
        
        let currentMission = 0;
        const missions = [
            { name: "🌆 KOTA HANCUR", bg: "#4a2e2e", enemyCount: 6, hasArtillery: true },
            { name: "🌲 HUTAN BAKAR", bg: "#2b4a2f", enemyCount: 8, hasArtillery: true },
            { name: "💀 SARANG TERAKHIR", bg: "#1e1a2f", enemyCount: 10, hasArtillery: true, boss: true }
        ];
        
        function startStory(){
            gamePhase = 'story';
            storyQueue = [...WAR_STORY];
            advanceStoryDialog();
        }
        function advanceStoryDialog(){
            if(storyQueue.length === 0){ startBattleMission(0); return; }
            const line = storyQueue.shift();
            document.getElementById('warDialog').innerHTML = `📢 ${line.speaker}: ${line.text}`;
            if(window.storyTimeout) clearTimeout(window.storyTimeout);
            window.storyTimeout = setTimeout(() => { if(gamePhase==='story') advanceStoryDialog(); }, 2800);
        }
        function skipStory(){ if(gamePhase==='story'){ if(window.storyTimeout) clearTimeout(window.storyTimeout); if(storyQueue.length) advanceStoryDialog(); else startBattleMission(0); } }
        
        // =============== GAME ENGINE (Battle Royale style) ===============
        let gameRunning = true, player, enemies=[], bullets=[], effects=[], particles=[], score=0, keys={}, mouse={x:500,y:300}, mouseLeftDown=false, shootCooldown=0, moveTarget=null, isSprinting=false, shake=0, walls=[];
        let craters = [], tankTracks = [];
        
        class WarGeneral {
            constructor(x,y){ this.x=x; this.y=y; this.size=24; this.hp=200; this.maxHp=200; this.baseSpeed=3.8; this.sprintSpeed=6.5; this.speed=this.baseSpeed; this.ammo=40; this.maxAmmo=40; this.reloading=false; this.reloadTimer=0; this.invincible=0; this.angle=0; this.anim=0; }
            update(){
                if(moveTarget){
                    let dx=moveTarget.x-this.x, dy=moveTarget.y-this.y, dist=Math.hypot(dx,dy);
                    if(dist>5){ let step=Math.min(this.speed,dist); let nx=this.x+dx/dist*step, ny=this.y+dy/dist*step; if(!this.collideWall(nx,ny)){ this.x=nx; this.y=ny; } else moveTarget=null; }
                    else moveTarget=null;
                }
                this.x=Math.min(Math.max(this.x,30),canvas.width-30); this.y=Math.min(Math.max(this.y,40),canvas.height-40);
                this.angle=Math.atan2(mouse.y-this.y, mouse.x-this.x);
                if(this.reloading){ this.reloadTimer--; if(this.reloadTimer<=0){ this.ammo=this.maxAmmo; this.reloading=false; addFloatingText(this.x,this.y-20,"RELOAD SIAP","#aaffaa"); } }
                if(this.invincible>0) this.invincible--;
                this.anim+=0.2;
                if(isSprinting && !this.reloading) this.speed=this.sprintSpeed; else this.speed=this.baseSpeed;
            }
            collideWall(nx,ny){ for(let w of walls) if(nx-this.size<w.x+w.w && nx+this.size>w.x && ny-this.size<w.y+w.h && ny+this.size>w.y) return true; return false; }
            shoot(){ if(this.reloading || this.ammo<=0 || shootCooldown>0) return; this.ammo--; shootCooldown=9; shake=3; bullets.push(new Bullet(this.x+Math.cos(this.angle)*this.size, this.y+Math.sin(this.angle)*this.size, this.angle, true, 18)); if(this.ammo<=0) this.reload(); }
            reload(){ if(this.reloading) return; this.reloading=true; this.reloadTimer=55; addFloatingText(this.x,this.y-15,"RELOAD...","#ffaa66"); }
            takeDamage(dmg){ if(this.invincible>0) return; this.hp-=dmg; this.invincible=25; shake=8; if(this.hp<=0) gameLose(); }
            draw(){
                ctx.save(); ctx.translate(this.x,this.y);
                ctx.fillStyle='#f39c12'; ctx.beginPath(); ctx.ellipse(0,0,20,24,0,0,Math.PI*2); ctx.fill();
                ctx.fillStyle='#c97e0a'; ctx.fillRect(-18,-14,36,8);
                ctx.fillStyle='white'; ctx.beginPath(); ctx.arc(-8,-6,5,0,Math.PI*2); ctx.arc(8,-6,5,0,Math.PI*2); ctx.fill();
                ctx.fillStyle='#000'; ctx.beginPath(); ctx.arc(-7,-5,2.5,0,Math.PI*2); ctx.arc(9,-5,2.5,0,Math.PI*2); ctx.fill();
                ctx.fillStyle='#e67e22'; ctx.fillRect(-12,6,24,5);
                if(isSprinting){ ctx.fillStyle='#ffff66'; ctx.font='bold 20px monospace'; ctx.fillText("💨",-12,-18); }
                ctx.save(); ctx.rotate(this.angle); ctx.fillStyle='#4a5c3c'; ctx.fillRect(14,-5,28,8); ctx.fillStyle='#ffaa33'; ctx.fillRect(38,-6,10,10); ctx.restore();
                ctx.restore();
            }
        }
        
        class EnemyUnit {
            constructor(x,y,type){ this.x=x; this.y=y; this.type=type; this.hp=(type==="heavy"?120:(type==="boss"?320:55)); this.maxHp=this.hp; this.size=(type==="heavy"?28:20); this.speed=1.4; this.shootTimer=Math.random()*40+25; this.angle=0; }
            update(){
                if(!player) return; let dx=player.x-this.x, dy=player.y-this.y, dist=Math.hypot(dx,dy); this.angle=Math.atan2(dy,dx);
                if(dist<300){ let moveX=dx/dist*this.speed, moveY=dy/dist*this.speed; this.x+=moveX; this.y+=moveY; }
                this.x=Math.min(Math.max(this.x,20),canvas.width-20); this.y=Math.min(Math.max(this.y,30),canvas.height-30);
                this.shootTimer--; if(this.shootTimer<=0 && dist<380){ bullets.push(new Bullet(this.x+Math.cos(this.angle)*this.size, this.y+Math.sin(this.angle)*this.size, this.angle, false, this.type==="heavy"?15:10)); this.shootTimer=(this.type==="heavy"?48:32); }
            }
            takeDamage(dmg){ this.hp-=dmg; if(this.hp<=0) return true; return false; }
            draw(){
                ctx.save(); ctx.translate(this.x,this.y);
                ctx.fillStyle='#5a3e2c'; ctx.beginPath(); ctx.ellipse(0,0,this.size-2,this.size,0,0,Math.PI*2); ctx.fill();
                ctx.fillStyle='#8b0000'; ctx.fillRect(-12,-14,24,6);
                ctx.fillStyle='#ff4444'; ctx.beginPath(); ctx.arc(-6,-5,4,0,Math.PI*2); ctx.arc(6,-5,4,0,Math.PI*2); ctx.fill();
                if(this.type==="heavy") ctx.fillStyle='#ffaa33', ctx.font='bold 18px monospace', ctx.fillText("💣",-8,-12);
                if(this.type==="boss") ctx.fillStyle='#ffaa00', ctx.font='bold 24px monospace', ctx.fillText("👑😾",-12,-16);
                ctx.restore();
                ctx.fillStyle='#440000'; ctx.fillRect(this.x-18,this.y-22,36,6);
                ctx.fillStyle='#ff5500'; ctx.fillRect(this.x-18,this.y-22,36*(this.hp/this.maxHp),6);
            }
        }
        
        class Bullet {
            constructor(x,y,angle,friendly,damage){ this.x=x; this.y=y; this.angle=angle; this.friendly=friendly; this.speed=friendly?11:7; this.life=80; this.damage=damage; }
            update(){ this.x+=Math.cos(this.angle)*this.speed; this.y+=Math.sin(this.angle)*this.speed; this.life--; if(this.x<0||this.x>canvas.width||this.y<0||this.y>canvas.height) this.life=0; for(let w of walls) if(this.x>w.x && this.x<w.x+w.w && this.y>w.y && this.y<w.y+w.h) this.life=0; }
            draw(){ ctx.fillStyle=this.friendly?'#ffcc44':'#ff4422'; ctx.beginPath(); ctx.arc(this.x,this.y,5,0,Math.PI*2); ctx.fill(); if(this.friendly) ctx.fillStyle='gold', ctx.beginPath(), ctx.arc(this.x-2,this.y-2,2,0,Math.PI*2), ctx.fill(); }
        }
        
        function addCrater(x,y){ craters.push({x,y}); }
        function addTankTrack(x,y){ tankTracks.push({x,y}); }
        function addSmoke(x,y){ effects.push({x,y, life:60, type:'smoke', size:12}); }
        function createExplosion(x,y){ for(let i=0;i<20;i++) particles.push({x,y, life:30, size:Math.random()*8+3, col:'#ff8844', vx:(Math.random()-0.5)*5, vy:(Math.random()-0.5)*5}); addCrater(x,y); addSmoke(x,y); }
        function addFloatingText(x,y,text,col){ particles.push({x,y, life:40, text, col}); }
        
        function spawnEnemies(missionIdx){
            let count = missions[missionIdx].enemyCount;
            for(let i=0;i<count;i++){
                let type='soldier';
                if(missionIdx===1 && i%3===0) type='heavy';
                if(missionIdx===2){ if(i===count-1) type='boss'; else if(i%2===0) type='heavy'; }
                let x = canvas.width-80-Math.random()*200, y = 80+Math.random()*400;
                enemies.push(new EnemyUnit(x,y,type));
            }
        }
        
        function startBattleMission(missionId){
            currentMission = missionId; gamePhase = 'battle'; gameRunning=true;
            walls = [{x:80,y:80,w:30,h:440},{x:890,y:80,w:30,h:440},{x:200,y:150,w:120,h:20},{x:680,y:400,w:140,h:20},{x:450,y:520,w:100,h:20}];
            for(let i=0;i<15;i++) addCrater(150+Math.random()*700, 80+Math.random()*450);
            for(let i=0;i<25;i++) addTankTrack(300+Math.random()*500, 200+Math.random()*300);
            player = new WarGeneral(120, 300);
            enemies = []; spawnEnemies(missionId);
            score = 0; moveTarget = null;
            updateUI();
            document.getElementById('warDialog').innerHTML = `🔥 MISI ${missionId+1}: ${missions[missionId].name} - HANCURKAN MUSUH! 🔥`;
        }
        
        function updateUI(){ if(player){ document.getElementById('hpStat').innerText = `${player.hp}/${player.maxHp}`; document.getElementById('ammoStat').innerText = `${player.ammo}/${player.maxAmmo}${player.reloading?' (R)':''}`; document.getElementById('scoreStat').innerText = score; } }
        function gameLose(){ gameRunning=false; gamePhase='story'; document.getElementById('warDialog').innerHTML = "💀 KEKALAHAN! Meowstar runtuh... Tekan F5 untuk memulai perang baru 💀"; }
        
        function updateBattle(){
            if(!gameRunning || gamePhase!=='battle') return;
            if(!player) return;
            player.update();
            for(let e of enemies) e.update();
            if(shootCooldown>0) shootCooldown--;
            if(mouseLeftDown && !player.reloading && player.ammo>0) player.shoot();
            
            for(let i=0;i<bullets.length;i++){
                bullets[i].update(); let hit=false;
                if(bullets[i].friendly){
                    for(let j=0;j<enemies.length;j++){
                        let e=enemies[j];
                        if(Math.hypot(bullets[i].x-e.x, bullets[i].y-e.y) < e.size+5){
                            hit=true;
                            if(e.takeDamage(bullets[i].damage)){
                                let addScore = e.type==='boss'? 800 : (e.type==='heavy'? 200 : 80);
                                score += addScore;
                                createExplosion(e.x,e.y);
                                enemies.splice(j,1);
                                updateUI();
                            }
                            break;
                        }
                    }
                } else {
                    if(Math.hypot(bullets[i].x-player.x, bullets[i].y-player.y) < player.size+4){
                        player.takeDamage(bullets[i].damage); hit=true; updateUI();
                    }
                }
                if(hit) bullets.splice(i,1), i--;
            }
            
            for(let i=0;i<effects.length;i++){ effects[i].life--; if(effects[i].type==='smoke') effects[i].size+=0.5; }
            effects = effects.filter(e=>e.life>0);
            particles = particles.filter(p=>{ p.life--; if(p.vx) p.x+=p.vx, p.y+=p.vy; return p.life>0; });
            
            if(enemies.length===0){
                if(currentMission+1 < missions.length){ currentMission++; startBattleMission(currentMission); }
                else { gameRunning=false; gamePhase='story'; document.getElementById('warDialog').innerHTML = "🏆 VICTORY! KERAJAAN CAKAR BESI RUNTUH! MEOWSTAR MENANG! 🏆"; }
            }
            if(player.hp<=0) gameLose();
            updateUI();
        }
        
        function drawBattlefield(){
            const m = missions[currentMission];
            ctx.fillStyle = m.bg; ctx.fillRect(0,0,canvas.width,canvas.height);
            for(let c of craters){ ctx.fillStyle='#2a1a0a'; ctx.beginPath(); ctx.ellipse(c.x,c.y,12,6,0,0,Math.PI*2); ctx.fill(); ctx.fillStyle='#4a2e1a'; ctx.beginPath(); ctx.ellipse(c.x,c.y,9,4,0,0,Math.PI*2); ctx.fill(); }
            for(let t of tankTracks){ ctx.fillStyle='#3e2a1c'; ctx.fillRect(t.x-8,t.y-3,18,6); for(let i=-1;i<=1;i++) ctx.fillRect(t.x-12+i*6,t.y-1,6,4); }
            for(let e of effects){ if(e.type==='smoke'){ ctx.globalAlpha = Math.min(1, e.life/40); ctx.fillStyle='#888888'; ctx.beginPath(); ctx.arc(e.x, e.y, e.size*0.7, 0, Math.PI*2); ctx.fill(); ctx.fillStyle='#aaaaaa'; ctx.beginPath(); ctx.arc(e.x-3, e.y-2, e.size*0.4, 0, Math.PI*2); ctx.fill(); ctx.globalAlpha=1; } }
            for(let w of walls){ ctx.fillStyle='#5d3a1a'; ctx.fillRect(w.x,w.y,w.w,w.h); ctx.fillStyle='#ad8a5c'; ctx.fillRect(w.x+4,w.y+4,w.w-8,w.h-8); }
            for(let b of bullets) b.draw();
            for(let e of enemies) e.draw();
            player.draw();
            for(let p of particles){ if(p.text){ ctx.fillStyle=p.col; ctx.font='bold 14px monospace'; ctx.fillText(p.text,p.x,p.y); } else { ctx.fillStyle=p.col; ctx.beginPath(); ctx.arc(p.x,p.y,p.size,0,Math.PI*2); ctx.fill(); } }
            if(moveTarget){ ctx.beginPath(); ctx.moveTo(player.x,player.y); ctx.lineTo(moveTarget.x,moveTarget.y); ctx.strokeStyle='#ffaa55'; ctx.setLineDash([5,8]); ctx.stroke(); ctx.setLineDash([]); ctx.fillStyle='#ffffaa'; ctx.beginPath(); ctx.arc(moveTarget.x,moveTarget.y,8,0,Math.PI*2); ctx.fill(); }
            if(shake>0) ctx.translate((Math.random()-0.5)*shake, (Math.random()-0.5)*shake), shake*=0.9;
            ctx.beginPath(); ctx.arc(mouse.x,mouse.y,12,0,Math.PI*2); ctx.strokeStyle='#ffcc44'; ctx.lineWidth=2; ctx.stroke();
            ctx.beginPath(); ctx.moveTo(mouse.x-20,mouse.y); ctx.lineTo(mouse.x-8,mouse.y); ctx.moveTo(mouse.x+8,mouse.y); ctx.lineTo(mouse.x+20,mouse.y);
            ctx.moveTo(mouse.x,mouse.y-20); ctx.lineTo(mouse.x,mouse.y-8); ctx.moveTo(mouse.x,mouse.y+8); ctx.lineTo(mouse.x,mouse.y+20); ctx.stroke();
        }
        
        function gameLoop(){
            if(gamePhase === 'battle'){ updateBattle(); drawBattlefield(); }
            else { ctx.fillStyle='#001133'; ctx.fillRect(0,0,canvas.width,canvas.height); ctx.font='bold 26px monospace'; ctx.fillStyle='#ffd966'; ctx.fillText("🔥 PERANG DUA NEGARA KUCING 🔥", canvas.width/2-280,100); ctx.font='16px monospace'; ctx.fillStyle='#bbddff'; ctx.fillText("Tekan SPASI untuk lanjut cerita dramatis", canvas.width/2-180,540); }
            requestAnimationFrame(gameLoop);
        }
        
        // =============== EVENT ===============
        function handleCanvasClick(e){
            const rect = canvas.getBoundingClientRect(), scaleX = canvas.width/rect.width, scaleY = canvas.height/rect.height;
            let cx = (e.clientX - rect.left) * scaleX, cy = (e.clientY - rect.top) * scaleY;
            cx = Math.min(Math.max(cx,20),canvas.width-20); cy = Math.min(Math.max(cy,20),canvas.height-20);
            if(e.button === 2){ if(gamePhase==='battle' && player && !player.reloading) moveTarget = { x: cx, y: cy }; e.preventDefault(); }
        }
        canvas.addEventListener('mousedown', (e) => { if(e.button===0) mouseLeftDown=true; handleCanvasClick(e); });
        canvas.addEventListener('mouseup', (e) => { if(e.button===0) mouseLeftDown=false; });
        canvas.addEventListener('mousemove', (e) => { const rect = canvas.getBoundingClientRect(); const scaleX = canvas.width/rect.width, scaleY = canvas.height/rect.height; mouse.x = (e.clientX - rect.left)*scaleX; mouse.y = (e.clientY - rect.top)*scaleY; });
        canvas.addEventListener('contextmenu', (e) => e.preventDefault());
        window.addEventListener('keydown', (e) => { const k=e.key.toLowerCase(); keys[k]=true; if(k===' ' && gamePhase==='story') skipStory(); if(k==='r' && gamePhase==='battle' && player) player.reload(); if(k==='shift' && gamePhase==='battle' && player && !player.reloading) isSprinting=true; });
        window.addEventListener('keyup', (e) => { const k=e.key.toLowerCase(); keys[k]=false; if(k==='shift') isSprinting=false; });
        document.getElementById('reloadBtn').addEventListener('click', () => { if(gamePhase==='battle' && player) player.reload(); });
        document.getElementById('sprintBtn').addEventListener('mousedown', () => { if(gamePhase==='battle' && player && !player.reloading) isSprinting=true; });
        document.getElementById('sprintBtn').addEventListener('mouseup', () => isSprinting=false);
        startStory(); gameLoop();
    })();
</script>
</body>
</html>
"""

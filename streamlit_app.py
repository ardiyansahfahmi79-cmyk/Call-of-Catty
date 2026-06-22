import streamlit as st
import streamlit.components.v1 as components

# Mengatur tampilan Streamlit agar Full Width dan menyembunyikan elemen bawaan Streamlit
st.set_page_config(page_title="Aerovulpis Terminal", layout="wide", initial_sidebar_state="collapsed")

# Menyembunyikan header dan footer bawaan Streamlit agar terasa seperti aplikasi mandiri
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 0rem; padding-bottom: 0rem;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Membungkus kode React ke dalam iframe HTML yang di-render oleh Babel
react_code = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        body { margin: 0; padding: 0; background: #070A12; }
        /* Kustomisasi scrollbar agar cocok dengan tema Terminal */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #070A12; }
        ::-webkit-scrollbar-thumb { background: #1A2540; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #00E1FF; }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect, useRef, useMemo, useCallback } = React;

        /* ==========================================================================
           AEROVULPIS TERMINAL — PROTOTYPE v4.1
           Cyberpunk Quantitative Trading Interface
           ========================================================================== */

        // ---------------------------------------------------------------------------
        // INSTRUMENTS
        // ---------------------------------------------------------------------------
        const INSTRUMENTS = {
          FOREX: [
            { label: "EURUSD", tv: "OANDA:EURUSD", td: "EUR/USD" },
            { label: "GBPUSD", tv: "OANDA:GBPUSD", td: "GBP/USD" },
            { label: "USDJPY", tv: "OANDA:USDJPY", td: "USD/JPY" },
            { label: "AUDUSD", tv: "OANDA:AUDUSD", td: "AUD/USD" },
            { label: "USDCHF", tv: "OANDA:USDCHF", td: "USD/CHF" },
          ],
          COMMODITIES: [
            { label: "XAUUSD", tv: "OANDA:XAUUSD", td: "XAU/USD" },
            { label: "XAGUSD", tv: "OANDA:XAGUSD", td: "XAG/USD" },
            { label: "WTIUSD", tv: "TVC:USOIL", td: "WTI/USD" },
            { label: "BRENT", tv: "TVC:UKOIL", td: "BRENT/USD" },
            { label: "NATGAS", tv: "TVC:NATURALGAS",td: "NATGAS" },
          ],
          "US STOCKS": [
            { label: "AAPL", tv: "NASDAQ:AAPL", td: "AAPL" },
            { label: "NVDA", tv: "NASDAQ:NVDA", td: "NVDA" },
            { label: "TSLA", tv: "NASDAQ:TSLA", td: "TSLA" },
            { label: "MSFT", tv: "NASDAQ:MSFT", td: "MSFT" },
            { label: "AMZN", tv: "NASDAQ:AMZN", td: "AMZN" },
          ],
          CRYPTO: [
            { label: "BTCUSD", tv: "COINBASE:BTCUSD", td: "BTC/USD" },
            { label: "ETHUSD", tv: "COINBASE:ETHUSD", td: "ETH/USD" },
            { label: "SOLUSD", tv: "COINBASE:SOLUSD", td: "SOL/USD" },
            { label: "BNBUSD", tv: "BINANCE:BNBUSDT", td: "BNB/USDT" },
            { label: "XRPUSD", tv: "COINBASE:XRPUSD", td: "XRP/USD" },
          ],
        };

        const TIMEFRAMES = ["15m","1h","4h","1D"];
        const TV_INTERVAL = { "15m":"15","1h":"60","4h":"240","1D":"D" };
        const TV_TA_INTERVAL = { "15m":"15m","1h":"1h","4h":"4h","1D":"1D" };

        const MINI_OPTIONS = [
          { label:"EURUSD", tv:"OANDA:EURUSD" },
          { label:"GBPUSD", tv:"OANDA:GBPUSD" },
          { label:"USDJPY", tv:"OANDA:USDJPY" },
          { label:"AUDUSD", tv:"OANDA:AUDUSD" },
          { label:"XAUUSD", tv:"OANDA:XAUUSD" },
          { label:"BTCUSD", tv:"COINBASE:BTCUSD" },
          { label:"NVDA",   tv:"NASDAQ:NVDA" },
          { label:"USDCHF", tv:"OANDA:USDCHF" },
        ];

        const DUMMY_TRADES = [
          { symbol:"EURUSD", dir:"BUY", entry:"1.14620", sl:"1.14280", tp1:"1.14950", tp2:"1.15300", tp3:"1.15700" },
          { symbol:"GBPUSD", dir:"SELL", entry:"1.32310", sl:"1.32650", tp1:"1.31980", tp2:"1.31600", tp3:"1.31150" },
          { symbol:"XAUUSD", dir:"BUY", entry:"2382.40", sl:"2371.00", tp1:"2394.00", tp2:"2406.50", tp3:"2420.00" },
          { symbol:"BTCUSD", dir:"BUY", entry:"67420.0", sl:"65800.0", tp1:"69000.0", tp2:"71500.0", tp3:"74200.0" },
        ];

        // ---------------------------------------------------------------------------
        // BLOOMBERG-CLASS MCT ENGINE
        // ---------------------------------------------------------------------------
        function seededLCG(seed) {
          let s = seed >>> 0;
          return () => {
            s = Math.imul(1664525, s) + 1013904223 >>> 0;
            return s / 0xFFFFFFFF;
          };
        }

        function savitzkyGolay(arr, windowLen = 25, polyOrder = 3) {
          const n = arr.length;
          const h = Math.floor(windowLen / 2);
          const result = new Float64Array(n);
          const coeffs = [];
          for (let j = -h; j <= h; j++) {
            const t = j / h;
            const c = (35 - 30 * t * t * 9 + 3 * Math.pow(t, 4) * 9) / 35;
            coeffs.push(c > 0 ? c : 0);
          }
          const coeffSum = coeffs.reduce((a, b) => a + b, 0);
          for (let i = 0; i < n; i++) {
            let val = 0, w = 0;
            for (let k = -h; k <= h; k++) {
              const idx = Math.max(0, Math.min(n - 1, i + k));
              const c = coeffs[k + h] / coeffSum;
              val += arr[idx] * c;
              w += c;
            }
            result[i] = val / w;
          }
          return result;
        }

        function toZScore(arr, lookback = 63) {
          const n = arr.length;
          const out = new Float64Array(n);
          for (let i = 0; i < n; i++) {
            const start = Math.max(0, i - lookback);
            const window = arr.slice(start, i + 1);
            const mean = window.reduce((a, b) => a + b, 0) / window.length;
            const std = Math.sqrt(window.reduce((a, b) => a + (b - mean) ** 2, 0) / window.length) || 1;
            out[i] = Math.max(-3, Math.min(3, (arr[i] - mean) / std)) / 3;
          }
          return out;
        }

        function generateMctBloomberg(seed, points = 120) {
          const rand = seededLCG(typeof seed === "string" ? seed.split("").reduce((h, c) => Math.imul(31, h) + c.charCodeAt(0) | 0, 0) : seed);
          let price = 1.1 + rand() * 0.5;
          const closes = [], highs = [], lows = [];
          for (let i = 0; i < points; i++) {
            const change = (rand() - 0.49) * 0.003;
            price = Math.max(0.5, price + change);
            const hl = Math.abs(rand() * 0.002);
            closes.push(price); highs.push(price + hl); lows.push(price - hl);
          }

          const rsi = new Float64Array(points);
          for (let i = 14; i < points; i++) {
            let up = 0, dn = 0, cnt = 0;
            for (let k = Math.max(0, i - 14); k < i; k++) {
              const d = closes[k + 1] - closes[k];
              if (d > 0) up += d; else dn -= d;
              cnt++;
            }
            rsi[i] = cnt ? 100 - 100 / (1 + (up / cnt) / ((dn / cnt) || 0.001)) : 50;
          }
          const rsiCentered = Array.from(rsi).map(v => v - 50);

          const ema = (arr, period) => {
            const k = 2 / (period + 1), out = [];
            let e = arr[0];
            for (const v of arr) { e = v * k + e * (1 - k); out.push(e); }
            return out;
          };
          const ema12 = ema(closes, 12), ema26 = ema(closes, 26);
          const macdLine = ema12.map((v, i) => v - ema26[i]);
          const signal9 = ema(macdLine, 9);
          const macdHist = macdLine.map((v, i) => v - signal9[i]);

          const atr = new Float64Array(points);
          for (let i = 1; i < points; i++) {
            const tr = Math.max(highs[i] - lows[i], Math.abs(highs[i] - closes[i - 1]), Math.abs(lows[i] - closes[i - 1]));
            atr[i] = i < 14 ? tr : (atr[i - 1] * 13 + tr) / 14;
          }
          const atrPct = Array.from(atr).map((v, i) => v / closes[i]);

          const ema20 = ema(closes, 20), ema50 = ema(closes, 50);
          const emaCross = ema20.map((v, i) => (v - ema50[i]) / closes[i]);

          const bbBw = new Float64Array(points);
          for (let i = 20; i < points; i++) {
            const sl = closes.slice(i - 20, i);
            const m = sl.reduce((a, b) => a + b, 0) / 20;
            const sd = Math.sqrt(sl.reduce((a, b) => a + (b - m) ** 2, 0) / 20);
            bbBw[i] = (2 * sd * 2) / m;
          }

          const stochK = new Float64Array(points);
          for (let i = 14; i < points; i++) {
            const hh = Math.max(...highs.slice(i - 14, i));
            const ll = Math.min(...lows.slice(i - 14, i));
            stochK[i] = hh !== ll ? (closes[i] - ll) / (hh - ll) * 100 - 50 : 0;
          }

          const willR = new Float64Array(points);
          for (let i = 14; i < points; i++) {
            const hh = Math.max(...highs.slice(i - 14, i));
            const ll = Math.min(...lows.slice(i - 14, i));
            willR[i] = hh !== ll ? ((hh - closes[i]) / (hh - ll)) * -100 + 50 : 0;
          }

          const roc = new Float64Array(points);
          for (let i = 10; i < points; i++) {
            roc[i] = (closes[i] - closes[i - 10]) / closes[i - 10] * 100;
          }

          const cci = new Float64Array(points);
          for (let i = 20; i < points; i++) {
            const tp = closes.slice(i - 20, i).map((c, k) => (c + highs[i - 20 + k] + lows[i - 20 + k]) / 3);
            const m = tp.reduce((a, b) => a + b, 0) / 20;
            const mad = tp.reduce((a, b) => a + Math.abs(b - m), 0) / 20;
            cci[i] = mad ? (tp[tp.length - 1] - m) / (0.015 * mad) : 0;
          }

          const zRsi = toZScore(rsiCentered);
          const zMacd = toZScore(Array.from(macdHist));
          const zAtr = toZScore(Array.from(atrPct));
          const zEma = toZScore(Array.from(emaCross));
          const zBb = toZScore(Array.from(bbBw));
          const zStoch = toZScore(Array.from(stochK).map(v => v / 50));
          const zWillR = toZScore(Array.from(willR).map(v => v / 50));
          const zRoc = toZScore(Array.from(roc));
          const zCci = toZScore(Array.from(cci).map(v => Math.max(-3, Math.min(3, v / 100))));

          const raw = new Float64Array(points);
          for (let i = 0; i < points; i++) {
            raw[i] = ( 0.20 * zRsi[i] + 0.18 * zMacd[i] + 0.12 * zEma[i] + 0.10 * zAtr[i] + 0.10 * zStoch[i] + 0.09 * zWillR[i] + 0.09 * zRoc[i] + 0.07 * zCci[i] + 0.05 * zBb[i]);
          }

          const scaled = Array.from(raw).map(v => Math.max(-100, Math.min(100, v * 100)));
          const smoothed = savitzkyGolay(scaled, 25, 3);
          return Array.from(smoothed).map(v => Math.max(-100, Math.min(100, v)));
        }

        // ---------------------------------------------------------------------------
        // MCT CHART COMPONENT
        // ---------------------------------------------------------------------------
        function MctChart({ seed }) {
          const data = useMemo(() => generateMctBloomberg(seed), [seed]);
          const W = 640, H = 220, PX = 10, PY = 12;
          const toX = i => PX + (i / (data.length - 1)) * (W - PX * 2);
          const toY = v => H / 2 - (v / 100) * (H / 2 - PY);

          const current = data[data.length - 1];
          const prev = data[data.length - 6] || 0;
          const isBull = current >= 0;
          const momentum = current - prev;
          const uid = seed.replace(/[^a-z0-9]/gi,"");

          const buildPath = filter => {
            let d = "", drawing = false;
            data.forEach((v, i) => {
              if (filter(v)) {
                const x = toX(i), y = toY(v);
                d += drawing ? ` L${x},${y}` : `M${x},${y}`;
                drawing = true;
              } else {
                drawing = false;
              }
            });
            return d;
          };

          const pathUp = buildPath(v => v >= 0);
          const pathDn = buildPath(v => v <= 0);

          const zoneY30 = toY(30), zoneY80 = toY(80);
          const zoneYn30 = toY(-30), zoneYn80 = toY(-80);
          const zeroY = toY(0);

          let regime = "NEUTRAL";
          if (current > 60) regime = "STRONG BULL";
          else if (current > 25) regime = "BULL";
          else if (current < -60) regime = "STRONG BEAR";
          else if (current < -25) regime = "BEAR";

          return (
            <div style={{ width:"100%" }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:4 }}>
                <div>
                  <div style={{ fontSize:9, letterSpacing:"2px", color:"#4A6080", marginBottom:2 }}>
                    MCT · COMPOSITE OSCILLATOR · 10-FACTOR
                  </div>
                  <div style={{ fontSize:11, color:"#8BA0C0", letterSpacing:"1px" }}>
                    RSI · MACD · ATR · EMA · BB · STOCH · WILLR · ROC · CCI
                  </div>
                </div>
                <div style={{ textAlign:"right" }}>
                  <div style={{ fontSize:22, fontWeight:"700", color: isBull?"#00E1FF":"#FF3D71", lineHeight:1, fontFamily:"monospace" }}>
                    {current >= 0 ? "+" : ""}{current.toFixed(2)}
                  </div>
                  <div style={{ fontSize:9, letterSpacing:"1.5px", color: isBull?"#0099BB":"#CC2255", marginTop:2 }}>
                    {regime} · {momentum >= 0 ? "▲" : "▼"} {Math.abs(momentum).toFixed(1)}
                  </div>
                </div>
              </div>

              <svg viewBox={`0 0 ${W} ${H}`} style={{ width:"100%", height:220, display:"block" }} preserveAspectRatio="none">
                <defs>
                  <linearGradient id={`ug${uid}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#00E1FF" stopOpacity="0.35"/>
                    <stop offset="100%" stopColor="#00E1FF" stopOpacity="0.02"/>
                  </linearGradient>
                  <linearGradient id={`dg${uid}`} x1="0" y1="1" x2="0" y2="0">
                    <stop offset="0%" stopColor="#FF3D71" stopOpacity="0.35"/>
                    <stop offset="100%" stopColor="#FF3D71" stopOpacity="0.02"/>
                  </linearGradient>
                  <filter id={`glow${uid}`}>
                    <feGaussianBlur stdDeviation="2.5" result="blur"/>
                    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                  </filter>
                </defs>

                <rect x={PX} y={zoneY80} width={W-PX*2} height={zoneY30-zoneY80} fill="rgba(0,225,255,0.04)"/>
                <rect x={PX} y={zoneYn30} width={W-PX*2} height={zoneYn80-zoneYn30} fill="rgba(255,61,113,0.04)"/>

                {[80,30,0,-30,-80].map(lvl => (
                  <g key={lvl}>
                    <line x1={PX} x2={W-PX} y1={toY(lvl)} y2={toY(lvl)} stroke={lvl===0?"rgba(255,255,255,0.6)":"rgba(42,53,80,0.8)"} strokeWidth={lvl===0?1.2:0.8} strokeDasharray={lvl===0?"none":"4,4"}/>
                    <text x={W-PX+3} y={toY(lvl)+3.5} fontSize="8.5" fill="#3A4A6A" fontFamily="monospace">{lvl}</text>
                  </g>
                ))}

                {[{y:toY(80),label:"OB EXTREME",col:"rgba(0,225,255,0.4)"},
                  {y:toY(30),label:"OB ZONE",col:"rgba(0,225,255,0.25)"},
                  {y:toY(-30),label:"OS ZONE",col:"rgba(255,61,113,0.25)"},
                  {y:toY(-80),label:"OS EXTREME",col:"rgba(255,61,113,0.4)"}].map(({y,label,col})=>(
                  <text key={label} x={PX+2} y={y-2} fontSize="7" fill={col} fontFamily="monospace">{label}</text>
                ))}

                <path d={`${pathUp} L${toX(data.length-1)},${zeroY} L${PX},${zeroY} Z`} fill={`url(#ug${uid})`}/>
                <path d={`${pathDn} L${toX(data.length-1)},${zeroY} L${PX},${zeroY} Z`} fill={`url(#dg${uid})`}/>
                <path d={pathUp} fill="none" stroke="#00E1FF" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" filter={`url(#glow${uid})`}/>
                <path d={pathDn} fill="none" stroke="#FF3D71" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" filter={`url(#glow${uid})`}/>

                <circle cx={toX(data.length-1)} cy={toY(current)} r="4" fill={isBull?"#00E1FF":"#FF3D71"} filter={`url(#glow${uid})`}/>
                <circle cx={toX(data.length-1)} cy={toY(current)} r="2" fill="#070A12"/>
              </svg>

              <div style={{ display:"flex", gap:3, marginTop:4, flexWrap:"wrap" }}>
                {[
                  {k:"RSI", v: data[data.length-1]*0.95 + (Math.random()-0.5)*5},
                  {k:"MACD", v: data[data.length-1]*0.88 + (Math.random()-0.5)*8},
                  {k:"TREND", v: data[data.length-1]*0.92 + (Math.random()-0.5)*6},
                  {k:"VOL", v: data[data.length-1]*0.70 + (Math.random()-0.5)*15},
                  {k:"STOCH", v: data[data.length-1]*0.85 + (Math.random()-0.5)*10},
                ].map(({k,v})=>{
                  const pct = Math.max(-100,Math.min(100,v));
                  const c = pct>0?"#00E1FF":"#FF3D71";
                  return (
                    <div key={k} style={{ flex:"1", minWidth:44, background:"#0A0E18", border:"1px solid #1A2238", borderRadius:4, padding:"4px 6px" }}>
                      <div style={{ fontSize:7.5, color:"#4A6080", letterSpacing:"1px", marginBottom:2 }}>{k}</div>
                      <div style={{ height:2, background:"#0E1422", borderRadius:1 }}>
                        <div style={{ width:`${Math.abs(pct)}%`, height:"100%", background:c, marginLeft:pct<0?`${100-Math.abs(pct)}%`:0, borderRadius:1 }}/>
                      </div>
                      <div style={{ fontSize:8, color:c, marginTop:2, textAlign:"right" }}>{pct>0?"+":""}{pct.toFixed(0)}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        }

        // ---------------------------------------------------------------------------
        // TV WIDGET HOOK
        // ---------------------------------------------------------------------------
        function useTvWidget(ref, src, config, deps = []) {
          useEffect(() => {
            const el = ref.current;
            if (!el) return;
            el.innerHTML = "";
            const w = document.createElement("div");
            w.className = "tradingview-widget-container__widget";
            el.appendChild(w);
            const s = document.createElement("script");
            s.type = "text/javascript";
            s.src = src;
            s.async = true;
            s.text = JSON.stringify(config);
            el.appendChild(s);
          }, deps);
        }

        // ---------------------------------------------------------------------------
        // MARKET OVERVIEW
        // ---------------------------------------------------------------------------
        function MarketOverviewWidget() {
          const ref = useRef(null);
          useTvWidget(ref, "https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js", {
            colorTheme:"dark", dateRange:"3M", locale:"en", isTransparent:true, showFloatingTooltip:false,
            plotLineColorGrowing:"rgba(0,225,255,1)", plotLineColorFalling:"rgba(255,61,113,1)",
            gridLineColor:"rgba(42,53,80,0)", scaleFontColor:"#4A6080",
            belowLineFillColorGrowing:"rgba(0,225,255,0.10)", belowLineFillColorFalling:"rgba(255,61,113,0.10)",
            belowLineFillColorGrowingBottom:"rgba(0,225,255,0)", belowLineFillColorFallingBottom:"rgba(255,61,113,0)",
            symbolActiveColor:"rgba(0,225,255,0.10)",
            tabs:[
              { title:"FOREX", symbols:[ {s:"FX:EURUSD",d:"EUR/USD"},{s:"FX:GBPUSD",d:"GBP/USD"}, {s:"FX:USDJPY",d:"USD/JPY"},{s:"FX:USDCHF",d:"USD/CHF"},{s:"FX:AUDUSD",d:"AUD/USD"} ]},
              { title:"CRYPTO", symbols:[ {s:"COINBASE:BTCUSD",d:"BTC/USD"},{s:"COINBASE:ETHUSD",d:"ETH/USD"}, {s:"COINBASE:SOLUSD",d:"SOL/USD"},{s:"BINANCE:BNBUSDT",d:"BNB/USDT"},{s:"COINBASE:XRPUSD",d:"XRP/USD"} ]},
              { title:"INDICES", symbols:[ {s:"FOREXCOM:SPXUSD",d:"S&P 500"},{s:"FOREXCOM:NSXUSD",d:"Nasdaq"},{s:"FOREXCOM:DJI",d:"Dow Jones"} ]},
              { title:"COMMODITIES", symbols:[ {s:"CMCMARKETS:GOLD",d:"Gold"},{s:"PYTH:WTI3!",d:"WTI Oil"},{s:"TVC:NATURALGAS",d:"Nat Gas"} ]},
            ], backgroundColor:"#070A12", width:"100%", height:"300", showSymbolLogo:true, showChart:true,
          }, []);
          return <div ref={ref} className="tv-container" style={{height:300}}/>;
        }

        // ---------------------------------------------------------------------------
        // MAIN CHART
        // ---------------------------------------------------------------------------
        const CHART_STYLES = [
          {label:"LINE", value:"3"}, {label:"CANDLES", value:"1"}, {label:"HEIKIN", value:"8"}, {label:"AREA", value:"9"}, {label:"BARS", value:"0"},
        ];
        function MainChartWidget({ symbol, interval, style, onStyle }) {
          const ref = useRef(null);
          const [open, setOpen] = useState(false);
          useEffect(() => {
            const el = ref.current;
            if (!el) return;
            el.innerHTML = "";
            const container = document.createElement("div");
            container.style.height = "340px";
            el.appendChild(container);
            const script = document.createElement("script");
            script.type = "text/javascript";
            script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
            script.async = true;
            script.text = JSON.stringify({
              autosize: true, symbol, interval: TV_INTERVAL[interval], timezone: "Etc/UTC", theme: "dark", style,
              locale: "en", backgroundColor: "#070A12", gridColor: "rgba(42,53,80,0.3)", hide_top_toolbar: false,
              hide_legend: false, allow_symbol_change: false, save_image: false, calendar: false, hide_volume: false,
              support_host: "https://www.tradingview.com",
            });
            el.appendChild(script);
          }, [symbol, interval, style]);

          const curLabel = CHART_STYLES.find(s => s.value === style)?.label || "LINE";
          return (
            <div className="panel-box" style={{minWidth:340}}>
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:8}}>
                <div style={{position:"relative"}}>
                  <button className="sel-btn" onClick={()=>setOpen(!open)}>
                    <span style={{color:"#00E1FF",fontSize:9,letterSpacing:"1px"}}>{curLabel}</span>
                    <span style={{color:"#3A4A6A",fontSize:9,marginLeft:4}}>▾</span>
                  </button>
                  {open && (
                    <div className="drop-menu">
                      {CHART_STYLES.map(s=>(
                        <div key={s.value} className={"drop-item"+(s.value===style?" active":"")} onClick={()=>{onStyle(s.value);setOpen(false);}}>
                          {s.label}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div style={{fontSize:9,color:"#3A4A6A",letterSpacing:"1px"}}>
                  {symbol.split(":")[1]} · {interval}
                </div>
              </div>
              <div ref={ref} style={{height:340}}/>
            </div>
          );
        }

        // ---------------------------------------------------------------------------
        // TECHNICAL GAUGE
        // ---------------------------------------------------------------------------
        function TechGaugeWidget({ symbol, interval }) {
          const ref = useRef(null);
          useTvWidget(ref, "https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js", {
            colorTheme:"dark", displayMode:"single", isTransparent:true, locale:"en",
            interval: TV_TA_INTERVAL[interval], width:"100%", height:"320", symbol, showIntervalTabs:true
          }, [symbol, interval]);
          return <div ref={ref} className="tv-container" style={{height:320}}/>;
        }

        // ---------------------------------------------------------------------------
        // MINI CHART
        // ---------------------------------------------------------------------------
        function MiniChart({ value, onChange }) {
          const ref = useRef(null);
          const [open, setOpen] = useState(false);
          useTvWidget(ref, "https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js", {
            symbol:value.tv, width:"100%", height:160, locale:"en", dateRange:"1M", colorTheme:"dark",
            isTransparent:true, autosize:true, largeChartUrl:"", chartOnly:false
          }, [value.tv]);
          return (
            <div className="panel-box" style={{minWidth:210}}>
              <div style={{position:"relative",marginBottom:6}}>
                <button className="sel-btn" style={{borderColor:"rgba(0,225,255,0.3)"}} onClick={()=>setOpen(!open)}>
                  <span style={{color:"#00E1FF",fontWeight:700,fontSize:10}}>{value.label}</span>
                  <span style={{color:"#3A4A6A",fontSize:9,marginLeft:4}}>▾</span>
                </button>
                {open && (
                  <div className="drop-menu">
                    {MINI_OPTIONS.map(opt=>(
                      <div key={opt.tv} className={"drop-item"+(opt.tv===value.tv?" active":"")} onClick={()=>{onChange(opt);setOpen(false);}}>
                        {opt.label}
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <div ref={ref} style={{height:160}}/>
            </div>
          );
        }

        // ---------------------------------------------------------------------------
        // ECONOMIC CALENDAR
        // ---------------------------------------------------------------------------
        function EconCalWidget() {
          const ref = useRef(null);
          useTvWidget(ref, "https://s3.tradingview.com/external-embedding/embed-widget-events.js", {
            colorTheme:"dark", isTransparent:true, width:"100%", height:380, locale:"en",
            importanceFilter:"0,1", countryFilter:"us,eu,gb,jp,au,ch,ca,cn"
          }, []);
          return <div ref={ref} className="tv-container" style={{height:380}}/>;
        }

        // ---------------------------------------------------------------------------
        // SCREENER
        // ---------------------------------------------------------------------------
        function ScreenerWidget() {
          const ref = useRef(null);
          useTvWidget(ref, "https://s3.tradingview.com/external-embedding/embed-widget-screener.js", {
            market:"forex", showToolbar:true, defaultColumn:"overview", defaultScreen:"general",
            isTransparent:true, locale:"en", colorTheme:"dark", width:"100%", height:380
          }, []);
          return <div ref={ref} className="tv-container" style={{height:380}}/>;
        }

        // ---------------------------------------------------------------------------
        // TOP STORIES
        // ---------------------------------------------------------------------------
        function TopStoriesWidget() {
          const ref = useRef(null);
          useTvWidget(ref, "https://s3.tradingview.com/external-embedding/embed-widget-timeline.js", {
            feedMode:"all_symbols", colorTheme:"dark", isTransparent:true, displayMode:"regular",
            width:"100%", height:420, locale:"en"
          }, []);
          return <div ref={ref} className="tv-container" style={{height:420}}/>;
        }

        // ---------------------------------------------------------------------------
        // AI ANALYSIS
        // ---------------------------------------------------------------------------
        function AiPanel({ pairLabel }) {
          const [mode, setMode] = useState("pair");
          const [text, setText] = useState("");
          const [loading, setLoading] = useState(false);
          const [result, setResult] = useState(null);

          const run = () => {
            setLoading(true); setResult(null);
            setTimeout(() => {
              setResult(mode==="pair"
                ? `[PROTOTYPE] Analisis teknikal ${pairLabel}: Bias jangka pendek bearish-netral. RSI mendekati 42 (mendekati oversold), MACD histogram menyempit menunjukkan penurunan tekanan jual. EMA-20 masih di bawah EMA-50, konfirmasi downtrend minor. ATR meningkat 12% — volatilitas naik. Pantau level support kritis untuk konfirmasi reversal. Rekomendasi: WAIT — tunggu konfirmasi bounce di S1 sebelum entry BUY.`
                : `[PROTOTYPE] Dampak berita terhadap ${pairLabel}: Sentimen risk-off meningkat jangka pendek. Potensi penguatan USD akibat data inflasi yang lebih tinggi dari ekspektasi. Volatilitas diprediksi naik di sesi New York. Pantau reaksi harga di 30 menit pertama setelah rilis.`
              );
              setLoading(false);
            }, 1200);
          };

          return (
            <div className="panel-box full" style={{display:"flex",flexDirection:"column",gap:10}}>
              <div style={{display:"flex",gap:8}}>
                {["pair","news"].map(m=>(
                  <button key={m} className={"mode-btn"+(mode===m?" active":"")} onClick={()=>{setMode(m);setResult(null);}}>
                    {m==="pair"?"ANALISIS PAIR":"ANALISIS NEWS"}
                  </button>
                ))}
              </div>
              <div style={{display:"flex",gap:8,alignItems:"center"}}>
                {mode==="news" && (
                  <input className="ai-input" placeholder="PASTE HEADLINE / KONTEKS BERITA..." value={text} onChange={e=>setText(e.target.value)}/>
                )}
                <button className="run-btn" onClick={run} disabled={loading||(mode==="news"&&!text.trim())}>
                  {loading?"PROCESSING...":"ANALISIS"}
                </button>
              </div>
              {result && <div className="ai-result">{result}</div>}
            </div>
          );
        }

        // ---------------------------------------------------------------------------
        // TRADE CARD
        // ---------------------------------------------------------------------------
        function TradeCard({ t }) {
          const buy = t.dir==="BUY";
          return (
            <div className="trade-card">
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:10}}>
                <span style={{fontSize:13,fontWeight:700,color:"#E8F1FF",letterSpacing:"1px"}}>{t.symbol}</span>
                <span style={{fontSize:9,padding:"3px 8px",borderRadius:3,fontWeight:700,letterSpacing:"1.5px", background:buy?"rgba(0,225,255,0.12)":"rgba(255,61,113,0.12)", color:buy?"#00E1FF":"#FF3D71",border:`1px solid ${buy?"rgba(0,225,255,0.3)":"rgba(255,61,113,0.3)"}`}}>
                  {t.dir}
                </span>
              </div>
              {[["ENTRY",t.entry,"#8BA0C0"],["SL",t.sl,"#FF3D71"], ["TP1",t.tp1,"#00E1FF"],["TP2",t.tp2,"#00B8CC"],["TP3",t.tp3,"#0090A0"]].map(([k,v,c])=>(
                <div key={k} style={{display:"flex",justifyContent:"space-between",padding:"3px 0", borderBottom:"1px solid #0E1422",fontSize:11}}>
                  <span style={{color:"#3A4A6A",letterSpacing:"1px",fontSize:9}}>{k}</span>
                  <span style={{color:c,fontWeight:k!=="ENTRY"?"600":"400"}}>{v}</span>
                </div>
              ))}
            </div>
          );
        }

        // ---------------------------------------------------------------------------
        // SCROLL ROW
        // ---------------------------------------------------------------------------
        function HRow({ children, minW=320 }) {
          return (
            <div className="h-row">
              {Array.isArray(children) ? children.map((c,i)=>(
                <div key={i} style={{minWidth:minW,flexShrink:0,scrollSnapAlign:"start"}}>{c}</div>
              )) : <div style={{minWidth:minW,flexShrink:0,scrollSnapAlign:"start"}}>{children}</div>}
            </div>
          );
        }

        // ---------------------------------------------------------------------------
        // DROPDOWN SELECTOR
        // ---------------------------------------------------------------------------
        function Selector({ value, options, onChange, width=130 }) {
          const [open,setOpen] = useState(false);
          return (
            <div style={{position:"relative"}}>
              <button className="sel-btn" style={{width}} onClick={()=>setOpen(!open)}>
                <span style={{color:"#C8D8F0",fontSize:11}}>{value}</span>
                <span style={{color:"#3A4A6A",fontSize:9,marginLeft:4}}>▾</span>
              </button>
              {open && (
                <div className="drop-menu" style={{minWidth:width}}>
                  {options.map(opt=>(
                    <div key={opt} className={"drop-item"+(opt===value?" active":"")} onClick={()=>{onChange(opt);setOpen(false);}}>
                      {opt}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        }

        // ---------------------------------------------------------------------------
        // APP ROOT (Diubah dari 'export default function' menjadi 'function' biasa)
        // ---------------------------------------------------------------------------
        function AerovulpisTerminal() {
          const [instrClass, setInstrClass] = useState("FOREX");
          const [pair, setPair] = useState(INSTRUMENTS.FOREX[0]);
          const [tf, setTf] = useState("15m");
          const [chartStyle, setChartStyle] = useState("3");
          const [miniA, setMiniA] = useState(MINI_OPTIONS[1]);
          const [miniB, setMiniB] = useState(MINI_OPTIONS[2]);
          const [miniC, setMiniC] = useState(MINI_OPTIONS[3]);

          const mctSeed = `${pair.label}-${tf}`;
          const pairs = INSTRUMENTS[instrClass];

          return (
            <div className="root">
              <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
                *{box-sizing:border-box;margin:0;padding:0;}
                .root{
                  background:#070A12;
                  background-image: radial-gradient(ellipse 60% 35% at 10% 0%,rgba(0,225,255,0.055),transparent),
                                    radial-gradient(ellipse 50% 30% at 90% 5%,rgba(168,85,247,0.055),transparent);
                  min-height:100vh; font-family:'Share Tech Mono','Courier New',monospace; color:#C8D8F0;
                  padding-bottom:40px; overflow-x:hidden;
                }
                /* ── TOPBAR ── */
                .topbar{ padding:16px 16px 12px; border-bottom:1px solid #111827; position:sticky;top:0;z-index:100; background:rgba(7,10,18,0.95); backdrop-filter:blur(12px); }
                .brand-line{ display:flex;align-items:baseline;gap:10px; }
                .brand-prefix{ font-size:8px;letter-spacing:3px;color:#1A3A5A; border:1px solid #1A3A5A;padding:2px 6px;border-radius:2px; }
                .brand-name{ font-size:18px;letter-spacing:3px;color:#E8F1FF;font-weight:700; }
                .brand-name .acc{color:#00E1FF;}
                .brand-ver{ font-size:8px;letter-spacing:2px;color:#2A4060;margin-left:2px; }
                .brand-tagline{ font-size:8px;letter-spacing:2.5px;color:#1A3A5A;margin-top:3px; }
                .ticker-strip{ display:flex;gap:16px;overflow-x:auto;padding:8px 0 4px; scrollbar-width:none;font-size:11px;border-top:1px solid #0E1422;margin-top:10px; }
                .ticker-strip::-webkit-scrollbar{display:none;}
                .tick{white-space:nowrap;color:#3A4A6A;}
                .tick .sym{color:#4A6080;font-size:9px;letter-spacing:"1px";}
                .tick .val.up{color:#00E1FF;}
                .tick .val.dn{color:#FF3D71;}
                .sel-row{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;position:relative;}
                /* ── PANELS ── */
                .panel-box{ background:#09111E; border:1px solid #111827; border-radius:8px; padding:12px; position:relative; overflow:hidden; }
                .panel-box::before{ content:"";position:absolute;top:0;left:0;right:0;height:1px; background:linear-gradient(90deg,transparent,rgba(0,225,255,0.15),transparent); }
                .panel-box.full{width:100%;}
                /* ── SECTION ── */
                .sec{padding:16px 16px 6px;}
                .sec-label{font-size:8px;letter-spacing:2.5px;color:#1A3060;margin-bottom:8px;}
                /* ── H-ROW ── */
                .h-row{ display:flex;gap:10px;overflow-x:auto;padding:0 16px 12px; scroll-snap-type:x mandatory;scrollbar-width:none; }
                .h-row::-webkit-scrollbar{display:none;}
                /* ── SELECTORS ── */
                .sel-btn{ background:#09111E;border:1px solid #1A2540;color:#C8D8F0; padding:7px 12px;border-radius:5px;font-size:11px; font-family:'Share Tech Mono','Courier New',monospace; cursor:pointer;display:flex;align-items:center;gap:4px; letter-spacing:0.5px; }
                .sel-btn:hover{border-color:#00E1FF22;}
                .drop-menu{ position:absolute;top:110%;left:0; background:#09111E;border:1px solid #1A2540;border-radius:6px; z-index:200;overflow:hidden; box-shadow:0 12px 40px rgba(0,0,0,0.7);min-width:120px; }
                .drop-item{ padding:9px 14px;font-size:11px;cursor:pointer; color:#8BA0C0;letter-spacing:0.5px; border-bottom:1px solid #0E1422; }
                .drop-item:last-child{border-bottom:none;}
                .drop-item:hover,.drop-item.active{ background:rgba(0,225,255,0.08);color:#00E1FF; }
                /* ── TV ── */
                .tv-container{width:100%;}
                .tradingview-widget-container{width:100%;}
                /* ── AI ── */
                .mode-btn{ flex:1;background:#07101C; border:1px solid #1A2540;color:#4A6080; padding:9px 6px;border-radius:5px;font-size:10px; font-family:inherit;cursor:pointer;letter-spacing:1px; }
                .mode-btn.active{ border-color:rgba(0,225,255,0.4);color:#00E1FF; background:rgba(0,225,255,0.06); }
                .ai-input{ flex:1;background:#07101C;border:1px solid #1A2540; color:#C8D8F0;padding:9px 12px;border-radius:5px; font-size:11px;font-family:inherit;letter-spacing:0.5px; }
                .ai-input::placeholder{color:#2A3A54;}
                .run-btn{ background:linear-gradient(135deg,rgba(0,225,255,0.85),rgba(168,85,247,0.85)); color:#030608;font-weight:700;border:none; padding:9px 18px;border-radius:5px;font-size:10px; cursor:pointer;font-family:inherit;letter-spacing:1.5px; white-space:nowrap; }
                .run-btn:disabled{opacity:0.3;cursor:not-allowed;}
                .ai-result{ background:#07101C;border:1px solid #1A2540; border-left:2px solid #00E1FF; padding:12px 14px;border-radius:5px; font-size:11px;line-height:1.7;color:#8BA0C0;letter-spacing:0.3px; }
                /* ── TRADE CARD ── */
                .trade-card{ background:#09111E;border:1px solid #111827; border-radius:8px;padding:12px;min-width:190px; position:relative;overflow:hidden; }
                .trade-card::before{ content:"";position:absolute;top:0;left:0;right:0;height:1px; background:linear-gradient(90deg,transparent,rgba(0,225,255,0.2),transparent); }
              `}</style>

              {/* ════════════ TOPBAR ════════════ */}
              <div className="topbar">
                <div className="brand-line">
                  <span className="brand-prefix">SYS</span>
                  <span className="brand-name">AERO<span className="acc">VULPIS</span>&nbsp;TERMINAL</span>
                  <span className="brand-ver">v4.1</span>
                </div>
                <div className="brand-tagline">QUANTITATIVE MARKET INTELLIGENCE SYSTEM · PROTOTYPE BUILD</div>
                <div className="ticker-strip">
                  {[{s:"EURUSD",v:"1.1465",up:true},{s:"GBPUSD",v:"1.3228",up:true},
                    {s:"USDJPY",v:"161.24",up:false},{s:"XAUUSD",v:"2382.4",up:true},
                    {s:"BTCUSD",v:"67420",up:true},{s:"NVDA",v:"131.80",up:false},
                    {s:"AUDUSD",v:"0.7010",up:false}].map(t=>(
                    <span key={t.s} className="tick">
                      <span className="sym">{t.s} </span>
                      <span className={"val "+(t.up?"up":"dn")}>{t.v}</span>
                    </span>
                  ))}
                </div>
                <div className="sel-row">
                  <Selector value={instrClass} options={Object.keys(INSTRUMENTS)} width={120} onChange={cls=>{setInstrClass(cls);setPair(INSTRUMENTS[cls][0]);}}/>
                  <Selector value={pair.label} options={pairs.map(p=>p.label)} width={110} onChange={lbl=>{setPair(pairs.find(p=>p.label===lbl));}}/>
                  <Selector value={tf} options={TIMEFRAMES} width={80} onChange={setTf}/>
                </div>
              </div>

              {/* ════════════ ROW 1: MCT + MARKET OVERVIEW ════════════ */}
              <div className="sec"><div className="sec-label">// MARKET INTELLIGENCE LAYER</div></div>
              <HRow minW={340}>
                <div className="panel-box" style={{minWidth:340}}>
                  <MctChart seed={mctSeed}/>
                </div>
                <div className="panel-box" style={{minWidth:340}}>
                  <MarketOverviewWidget/>
                </div>
              </HRow>

              {/* ════════════ ROW 2: CHART + GAUGE ════════════ */}
              <div className="sec"><div className="sec-label">// CHART · {pair.label} · {tf}</div></div>
              <HRow minW={340}>
                <MainChartWidget symbol={pair.tv} interval={tf} style={chartStyle} onStyle={setChartStyle}/>
                <div className="panel-box" style={{minWidth:300}}>
                  <TechGaugeWidget symbol={pair.tv} interval={tf}/>
                </div>
              </HRow>

              {/* ════════════ ROW 3: MINI CHARTS ════════════ */}
              <div className="sec"><div className="sec-label">// MULTI-PAIR MONITOR</div></div>
              <HRow minW={210}>
                <MiniChart value={miniA} onChange={setMiniA}/>
                <MiniChart value={miniB} onChange={setMiniB}/>
                <MiniChart value={miniC} onChange={setMiniC}/>
              </HRow>

              {/* ════════════ ROW 4: CALENDAR + SCREENER ════════════ */}
              <div className="sec"><div className="sec-label">// FUNDAMENTAL DATA · PENYARING</div></div>
              <HRow minW={340}>
                <div className="panel-box" style={{minWidth:340}}>
                  <EconCalWidget/>
                </div>
                <div className="panel-box" style={{minWidth:340}}>
                  <ScreenerWidget/>
                </div>
              </HRow>

              {/* ════════════ ROW 5: AI ANALYSIS ════════════ */}
              <div className="sec"><div className="sec-label">// AI INTELLIGENCE ENGINE</div></div>
              <div style={{padding:"0 16px 12px"}}>
                <AiPanel pairLabel={pair.label}/>
              </div>

              {/* ════════════ ROW 6: TRADE SETUP ════════════ */}
              <div className="sec"><div className="sec-label">// ACTIVE TRADE SIGNALS</div></div>
              <HRow minW={190}>
                {DUMMY_TRADES.map(t=><TradeCard key={t.symbol} t={t}/>)}
              </HRow>

              {/* ════════════ ROW 7: TOP STORIES ════════════ */}
              <div className="sec"><div className="sec-label">// MARKET INTELLIGENCE · NEWS FEED</div></div>
              <div style={{padding:"0 16px 12px"}}>
                <div className="panel-box full"><TopStoriesWidget/></div>
              </div>
            </div>
          );
        }

        // Mount the React app ke div #root
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<AerovulpisTerminal />);
    </script>
</body>
</html>
"""

# Render React/HTML di dalam komponen Streamlit dengan tinggi yang cukup agar tidak terpotong
components.html(react_code, height=3000, scrolling=True)

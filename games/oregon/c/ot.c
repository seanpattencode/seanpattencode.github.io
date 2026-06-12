/* OREGON TRAIL (1978) — C port of oregon_trail.py, byte-identical transcripts
   (verified vs the Python original with injected RNG over hundreds of seeds).
   wasm:   clang --target=wasm32 -O2 -nostdlib -Wl,--no-entry \
             -Wl,--export=ot_boot -Wl,--export=ot_feed -Wl,--export=ot_in -o ot.wasm ot.c
   native: cc -DNATIVE -O2 -o ot_native ot.c   (replay harness on stdin: "ms\ttext") */
#include <stdint.h>
typedef uint32_t u32; typedef int64_t i64; typedef uint64_t u64;

#ifdef NATIVE
#include <stdio.h>
static void js_print(const char *p, int n){ fwrite(p, 1, (size_t)n, stdout); }
#else
__attribute__((import_module("env"), import_name("p"))) void js_print(const char *p, int n);
void *memset(void *d, int c, unsigned long n){ char *p = d; while (n--) *p++ = (char)c; return d; }
void *memcpy(void *d, const void *s, unsigned long n){ char *p = d; const char *q = s; while (n--) *p++ = *q++; return d; }
unsigned long strlen(const char *s){ unsigned long n = 0; while (s[n]) n++; return n; }
#endif

/* ---- rng: xorshift128 seeded by lowbias32 splitmix, identical in py/js/c ---- */
static u32 rs0, rs1, rs2, rs3, smx;
static u32 sm(void){ smx += 0x9e3779b9u; u32 t = smx; t ^= t >> 16; t *= 0x21f0aaadu; t ^= t >> 15; t *= 0x735a2d97u; t ^= t >> 15; return t; }
static double rnd(void){ u32 t = rs0 ^ (rs0 << 11); rs0 = rs1; rs1 = rs2; rs2 = rs3; rs3 = rs3 ^ (rs3 >> 19) ^ t ^ (t >> 8); return rs3 / 4294967296.0; }

/* ---- output ---- */
static void S(const char *s){ int n = 0; while (s[n]) n++; js_print(s, n); }
static void NL(void){ js_print("\n", 1); }
static void LN(const char *s){ S(s); NL(); }
static void PI(i64 v){ char b[24]; int i = 24, neg = v < 0; u64 u = neg ? (u64)-v : (u64)v; do { b[--i] = (char)('0' + u % 10); u /= 10; } while (u); if (neg) b[--i] = '-'; js_print(b + i, 24 - i); }
static int slen(const char *s){ int n = 0; while (s[n]) n++; return n; }
static void SP(int n){ while (n-- > 0) js_print(" ", 1); }
static void PAD(const char *s){ S(s); SP(15 - slen(s)); }
static void PADI(i64 v){ char b[24]; int i = 24; u64 u = v < 0 ? (u64)-v : (u64)v; do { b[--i] = (char)('0' + u % 10); u /= 10; } while (u); if (v < 0) b[--i] = '-'; js_print(b + i, 24 - i); SP(15 - (24 - i)); }

/* ---- state ---- */
static double oxen, bullets, cloth, food, misc, cash, mile, milePrev;
static int turn, skill, eat, fortItem, over;
static int injury, illS, spass, bluem, blizz, fortOpt, dispFlag;
enum { ACTION, FORT, SHOOT, EAT, FMIN, FFAN, FKIN, OVER };
enum { HUNT, BANDITS, ANIMALS };
static int st, sctx, sword;
static const char *WORDS[4] = {"BANG", "BLAM", "POW", "WHAM"};
static const int EV[15] = {6, 11, 13, 15, 17, 22, 32, 35, 37, 42, 44, 54, 64, 69, 95};
static const char *DATES[20] = {"MARCH 29","APRIL 12","APRIL 26","MAY 10","MAY 24","JUNE 7","JUNE 21","JULY 5","JULY 19","AUGUST 2","AUGUST 16","AUGUST 31","SEPTEMBER 13","SEPTEMBER 27","OCTOBER 11","OCTOBER 25","NOVEMBER 8","NOVEMBER 22","DECEMBER 6","DECEMBER 20"};
static const char *DOW[7] = {"MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY","SUNDAY"};
static i64 T(double d){ return (i64)d; }
static double mx0(double d){ return d > 0 ? d : 0; }

/* python float(): [+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?, whitespace-trimmed */
static int pyfloat(const char *s, int len, double *out){
    int i = 0, e = len;
    while (i < e && (s[i] == ' ' || s[i] == '\t' || s[i] == '\n' || s[i] == '\r')) i++;
    while (e > i && (s[e-1] == ' ' || s[e-1] == '\t' || s[e-1] == '\n' || s[e-1] == '\r')) e--;
    if (i >= e) return 0;
    int neg = 0;
    if (s[i] == '+' || s[i] == '-'){ neg = s[i] == '-'; i++; }
    double acc = 0; int digits = 0, scale = 0;
    while (i < e && s[i] >= '0' && s[i] <= '9'){ acc = acc * 10 + (s[i] - '0'); digits++; i++; }
    if (i < e && s[i] == '.'){
        i++;
        while (i < e && s[i] >= '0' && s[i] <= '9'){ acc = acc * 10 + (s[i] - '0'); digits++; scale++; i++; }
    }
    if (!digits) return 0;
    int ex = 0, exneg = 0;
    if (i < e && (s[i] == 'e' || s[i] == 'E')){
        i++;
        if (i < e && (s[i] == '+' || s[i] == '-')){ exneg = s[i] == '-'; i++; }
        if (i >= e || s[i] < '0' || s[i] > '9') return 0;
        while (i < e && s[i] >= '0' && s[i] <= '9'){ ex = ex * 10 + (s[i] - '0'); i++; }
    }
    if (i != e) return 0;
    int pw = (exneg ? -ex : ex) - scale;
    double den = 1;
    if (pw < 0){ while (pw++) den *= 10; acc /= den; }
    else { while (pw--) acc *= 10; }
    *out = neg ? -acc : acc;
    return 1;
}

static void victory(void);
static void startTurn(void);
static void postEvent(void);

static void askAction(void){
    if (food < 13) LN("YOU'D BETTER DO SOME HUNTING OR BUY FOOD SOON!!!!");
    if (fortOpt){ S("DO YOU WANT TO (1) STOP AT THE NEXT FORT, (2) HUNT, "); LN("OR (3) CONTINUE"); }
    else LN("DO YOU WANT TO (1) HUNT, OR (2) CONTINUE");
    st = ACTION;
}
static void doShoot(int ctx){ sword = (int)T(rnd() * 4); S("TYPE "); LN(WORDS[sword]); st = SHOOT; sctx = ctx; }
static int die(const char *cause, const char *type){
    LN(cause);
    if (type){ S("YOU DIED OF "); LN(type); }
    else if (injury) LN("YOU DIED OF INJURIES");
    NL(); LN("DUE TO YOUR UNFORTUNATE SITUATION, THERE ARE A FEW"); LN("FORMALITIES WE MUST GO THROUGH"); NL();
    S("WOULD YOU LIKE A MINISTER? "); st = FMIN;
    return 1;
}
static void eating(void){
    if (food < 13){ die("YOU RAN OUT OF FOOD AND STARVED TO DEATH", 0); return; }
    LN("DO YOU WANT TO EAT (1) POORLY (2) MODERATELY"); S("OR (3) WELL"); S("? "); st = EAT;
}
static int checkIllness(void){
    if (100 * rnd() < 10 + 35 * (eat - 1)) return 0;
    if (100 * rnd() < 100 - (40 / (double)(1 << (2 * (eat - 1))))){
        if (rnd() < 0.5){ LN("MILD ILLNESS---MEDICINE USED"); mile -= 5; misc -= 2; }
        else { LN("BAD ILLNESS---MEDICINE USED"); mile -= 5; misc -= 2; }
    } else { LN("SERIOUS ILLNESS---"); LN("YOU MUST STOP FOR MEDICAL ATTENTION"); misc -= 10; illS = 1; }
    if (misc < 0) return die("YOU RAN OUT OF MEDICAL SUPPLIES", "PNEUMONIA");
    if (blizz) blizz = 0;
    return 0;
}
static int blizzard(void){
    LN("BLIZZARD IN MOUNTAIN PASS--TIME AND SUPPLIES LOST");
    blizz = 1; food -= 25; misc -= 10; bullets -= 300; mile -= 30 + 40 * rnd();
    if (cloth < 18 + 2 * rnd()) return checkIllness();
    return 0;
}
static int randomEvent(void){           /* 0 done, 1 died, 2 waiting on shoot */
    double r1 = 100 * rnd(); int e = 15;
    for (int i = 0; i < 15; i++) if (r1 <= EV[i]){ e = i; break; }
    if (e == 0){ LN("WAGON BREAKS DOWN--LOSE TIME AND SUPPLIES FIXING IT"); mile -= 15 + 5 * rnd(); misc -= 8; }
    else if (e == 1){ LN("OX INJURES LEG---SLOWS YOU DOWN REST OF TRIP"); mile -= 25; oxen -= 20; }
    else if (e == 2){ LN("BAD LUCK---YOUR DAUGHTER BROKE HER ARM"); LN("YOU HAD TO STOP AND USE SUPPLIES TO MAKE A SLING"); mile -= 5 + 4 * rnd(); misc -= 2 + 3 * rnd(); }
    else if (e == 3){ LN("OX WANDERS OFF---SPEND TIME LOOKING FOR IT"); mile -= 17; }
    else if (e == 4){ LN("YOUR SON GETS LOST---SPEND HALF THE DAY LOOKING FOR HIM"); mile -= 10; }
    else if (e == 5){ LN("UNSAFE WATER--LOSE TIME LOOKING FOR CLEAN SPRING"); mile -= 10 * rnd() + 2; }
    else if (e == 6){
        if (mile <= 950){ LN("HEAVY RAINS---TIME AND SUPPLIES LOST"); food -= 10; bullets -= 500; misc -= 15; mile -= 10 * rnd() + 5; }
        else {
            S("COLD WEATHER---BRRRRRRR!--YOU ");
            int bad = cloth < 22 + 4 * rnd();
            if (bad) S("DON'T ");
            LN("HAVE ENOUGH CLOTHING TO KEEP YOU WARM");
            if (bad && checkIllness()) return 1;
        }
    }
    else if (e == 7){ LN("BANDITS ATTACK"); doShoot(BANDITS); return 2; }
    else if (e == 8){ LN("THERE WAS A FIRE IN YOUR WAGON--FOOD AND SUPPLIES DAMAGE!"); food -= 40; bullets -= 400; misc -= rnd() * 8 + 3; mile -= 15; }
    else if (e == 9){ LN("LOSE YOUR WAY IN HEAVY FOG---TIME IS LOST"); mile -= 10 + 5 * rnd(); }
    else if (e == 10){
        LN("YOU KILLED A POISONOUS SNAKE AFTER IT BIT YOU"); bullets -= 10; misc -= 5;
        if (misc < 0) return die("YOU DIE OF SNAKEBITE SINCE YOU HAVE NO MEDICINE", 0);
    }
    else if (e == 11){ LN("WAGON GETS SWAMPED FORDING RIVER--LOSE FOOD AND CLOTHES"); food -= 30; cloth -= 20; mile -= 20 + 20 * rnd(); }
    else if (e == 12){ LN("WILD ANIMALS ATTACK!"); doShoot(ANIMALS); return 2; }
    else if (e == 13){ LN("HAIL STORM---SUPPLIES DAMAGED"); mile -= 5 + rnd() * 10; bullets -= 200; misc -= 4 + rnd() * 3; }
    else if (e == 14){
        if (eat == 1){ if (checkIllness()) return 1; }
        else if (eat == 3){ if (rnd() < 0.5 && checkIllness()) return 1; }
        else { if (rnd() <= 0.25 && checkIllness()) return 1; }
    }
    else { LN("HELPFUL INDIANS SHOW YOU WHERE TO FIND MORE FOOD"); food += 14; }
    return 0;
}
static void postEvent(void){
    if (mile > 950){
        double t = mile / 100 - 15;
        if (rnd() * 10 > 9 - ((t * t + 72) / (t * t + 12))){
            LN("RUGGED MOUNTAINS");
            if (rnd() <= 0.1){ LN("YOU GOT LOST---LOSE VALUABLE TIME TRYING TO FIND TRAIL!"); mile -= 60; }
            else if (rnd() <= 0.11){ LN("WAGON DAMAGED!---LOSE TIME AND SUPPLIES"); misc -= 5; bullets -= 200; mile -= 20 + 30 * rnd(); }
            else { LN("THE GOING GETS SLOW"); mile -= 45 + rnd() / 0.02; }
        }
        if (!spass){
            spass = 1;
            if (rnd() >= 0.8) LN("YOU MADE IT SAFELY THROUGH SOUTH PASS--NO SNOW");
            else if (blizzard()) return;
        }
        if (mile >= 1700 && !bluem){
            bluem = 1;
            if (rnd() >= 0.7){} else if (blizzard()) return;
        }
        if (mile <= 950) dispFlag = 1;
    }
    milePrev = mile; turn += 1; fortOpt = !fortOpt;
    startTurn();
}
static void startTurn(void){
    if (mile >= 2040){ victory(); return; }
    if (turn >= 20){ LN("YOU HAVE BEEN ON THE TRAIL TOO LONG ------"); LN("YOUR FAMILY DIES IN THE FIRST BLIZZARD OF WINTER"); st = OVER; over = 1; return; }
    NL(); S("MONDAY "); S(DATES[turn]); LN(" 1847"); NL();
    food = mx0(food); bullets = mx0(bullets); cloth = mx0(cloth); misc = mx0(misc);
    food = (double)T(food); bullets = (double)T(bullets); cloth = (double)T(cloth); misc = (double)T(misc); cash = (double)T(cash); mile = (double)T(mile);
    if (illS || injury){
        cash -= 20;
        if (cash < 0){ die("YOU CAN'T AFFORD A DOCTOR", 0); return; }
        LN("DOCTOR'S BILL IS $20"); illS = 0; injury = 0;
    }
    if (dispFlag){ LN("TOTAL MILEAGE IS 950"); dispFlag = 0; }
    else { S("TOTAL MILEAGE IS "); PI(T(mile)); NL(); }
    PAD("FOOD"); PAD("BULLETS"); PAD("CLOTHING"); PAD("MISC. SUPP."); PAD("CASH"); NL();
    PADI(T(food)); PADI(T(bullets)); PADI(T(cloth)); PADI(T(misc)); PADI(T(cash)); NL();
    askAction();
}
static void victory(void){
    double diff = mile - milePrev;
    double fraction = diff == 0 ? 1.0 : (2040 - milePrev) / diff;
    food += (1 - fraction) * (8 + 5 * eat);
    NL(); LN("YOU FINALLY ARRIVED AT OREGON CITY"); LN("AFTER 2040 LONG MILES---HOORAY!!!!!"); LN("A REAL PIONEER!"); NL();
    i64 df = T(fraction * 14), total = turn * 14 + df;
    S(DOW[(df + 1) % 7]); S(" ");
    const char *m; i64 d;
    if (total <= 124){ m = "JULY"; d = total - 93; }
    else if (total <= 155){ m = "AUGUST"; d = total - 124; }
    else if (total <= 185){ m = "SEPTEMBER"; d = total - 155; }
    else if (total <= 216){ m = "OCTOBER"; d = total - 185; }
    else if (total <= 246){ m = "NOVEMBER"; d = total - 216; }
    else { m = "DECEMBER"; d = total - 246; }
    S(m); S(" "); PI(d); LN(" 1847"); NL();
    PAD("FOOD"); PAD("BULLETS"); PAD("CLOTHING"); PAD("MISC. SUPP."); PAD("CASH"); NL();
    i64 ff = T(food), fb = T(bullets), fc = T(cloth), fm = T(misc), fca = T(cash);
    PADI(ff > 0 ? ff : 0); PADI(fb > 0 ? fb : 0); PADI(fc > 0 ? fc : 0); PADI(fm > 1 ? fm : 1); PADI(fca > 0 ? fca : 0); NL();
    NL();
    SP(11); LN("PRESIDENT JAMES K. POLK SENDS YOU HIS");
    SP(17); LN("HEARTIEST CONGRATULATIONS"); NL();
    SP(11); LN("AND WISHES YOU A PROSPEROUS LIFE AHEAD"); NL();
    SP(22); LN("AT YOUR NEW HOME");
    st = OVER; over = 1;
}
static void fortAsk(void){
    static const char *L[4] = {"FOOD", "AMMUNITION", "CLOTHING", "MISCELLANEOUS SUPPLIES"};
    S(L[fortItem]); S("? ");
}

void ot_boot(u32 seed){
    smx = seed;
    u32 y = sm(), z = sm(), w = sm(), x = sm();
    rs0 = x; rs1 = y; rs2 = z; rs3 = w;
    oxen = bullets = cloth = food = misc = cash = mile = milePrev = 0;
    turn = 0; skill = 2; eat = 0; fortItem = 0; over = 0;
    injury = illS = spass = bluem = blizz = dispFlag = 0; fortOpt = 1;
    NL(); NL(); LN("YOUR WAGON HAS BEEN STOCKED WITH SUPPLIES:"); NL();
    oxen = 250; food = 150; double ammo = 75; cloth = 75; misc = 50;
    bullets = 50 * ammo; cash = 700 - (oxen + food + ammo + cloth + misc);
    S("  OXEN TEAM: $"); PI(T(oxen)); NL();
    S("  FOOD: $"); PI(T(food)); NL();
    S("  AMMUNITION: $"); PI(T(ammo)); S(" ("); PI(T(bullets)); LN(" BULLETS)");
    S("  CLOTHING: $"); PI(T(cloth)); NL();
    S("  MISCELLANEOUS SUPPLIES: $"); PI(T(misc)); NL(); NL();
    S("CASH ON HAND: $"); PI(T(cash)); NL(); NL();
    LN("MONDAY MARCH 29 1847"); NL();
    startTurn();
}

static char inbuf[256];
char *ot_in(void){ return inbuf; }
int ot_over(void){ return over; }

static int ieq(const char *a, int alen, const char *b){  /* strip().upper() == b */
    int i = 0, e = alen;
    while (i < e && (a[i] == ' ' || a[i] == '\t' || a[i] == '\n' || a[i] == '\r')) i++;
    while (e > i && (a[e-1] == ' ' || a[e-1] == '\t' || a[e-1] == '\n' || a[e-1] == '\r')) e--;
    int j = 0;
    for (; i < e && b[j]; i++, j++){
        char c = a[i]; if (c >= 'a' && c <= 'z') c = (char)(c - 32);
        if (c != b[j]) return 0;
    }
    return i == e && !b[j];
}

void ot_feed(int len, double ms){
    const char *line = inbuf;
    if (st == ACTION){
        double v;
        if (!pyfloat(line, len, &v)){ LN("PLEASE ENTER A NUMBER"); return; }
        double hi = fortOpt ? 3 : 2;
        if (v < 1 || v > hi){ LN(v < 1 ? "NOT ENOUGH" : "TOO MUCH"); return; }
        i64 c = T(v);
        if (!fortOpt){
            if (c == 1){
                if (bullets <= 39){ LN("TOUGH---YOU NEED MORE BULLETS TO GO HUNTING"); askAction(); return; }
                c = 2;
            } else c = 3;
        }
        if (c == 1){ LN("ENTER WHAT YOU WISH TO SPEND ON THE FOLLOWING"); fortItem = 0; fortAsk(); st = FORT; }
        else if (c == 2){
            if (bullets <= 39){ LN("TOUGH---YOU NEED MORE BULLETS TO GO HUNTING"); eating(); }
            else { mile -= 45; doShoot(HUNT); }
        }
        else eating();
        return;
    }
    if (st == FORT){
        double v;
        if (!pyfloat(line, len, &v)){ LN("PLEASE ENTER A NUMBER"); S("? "); return; }
        if (v < 0){ LN("NOT ENOUGH"); S("? "); return; }
        double amt = v;
        cash -= amt;
        if (cash < 0){ LN("YOU DON'T HAVE THAT MUCH--KEEP YOUR SPENDING DOWN"); LN("YOU MISS YOUR CHANCE TO SPEND ON THAT ITEM"); cash += amt; amt = 0; }
        if (fortItem == 0) food += (2.0 / 3.0) * amt;
        else if (fortItem == 1) bullets = (double)T(bullets + (2.0 / 3.0) * amt * 50);
        else if (fortItem == 2) cloth += (2.0 / 3.0) * amt;
        else misc += (2.0 / 3.0) * amt;
        fortItem += 1;
        if (fortItem < 4){ fortAsk(); return; }
        mile -= 45; eating(); return;
    }
    if (st == SHOOT){
        i64 rt = T(ms);
        double score = (rt / 100.0) - (skill - 1);
        NL();
        if (!ieq(line, len, WORDS[sword])) score = 9;
        i64 sc = T(score); if (sc < 0) sc = 0;
        if (sctx == HUNT){
            if (sc <= 1){ LN("RIGHT BETWEEN THE EYES---YOU GOT A BIG ONE!!!!"); LN("FULL BELLIES TONIGHT!"); food += 52 + rnd() * 6; bullets -= 10 + T(rnd() * 4); }
            else if (100 * rnd() < 13 * (double)sc) LN("YOU MISSED---AND YOUR DINNER GOT AWAY.....");
            else { LN("NICE SHOT--RIGHT ON TARGET--GOOD EATIN' TONIGHT!!"); food += 48 - 2 * (double)sc; bullets -= 10 + 3 * (double)sc; }
            eating();
        } else if (sctx == BANDITS){
            bullets -= 20 * (double)sc;
            if (bullets < 0){ LN("YOU RAN OUT OF BULLETS---THEY GET LOTS OF CASH"); cash = cash / 3; }
            else if (sc <= 1){ LN("QUICKEST DRAW OUTSIDE OF DODGE CITY!!!"); LN("YOU GOT 'EM!"); }
            else {
                LN("YOU GOT SHOT IN THE LEG AND THEY TOOK ONE OF YOUR OXEN");
                injury = 1; LN("BETTER HAVE A DOC LOOK AT YOUR WOUND"); misc -= 5; oxen -= 20;
            }
            postEvent();
        } else {
            if (bullets <= 39){
                LN("YOU WERE TOO LOW ON BULLETS--"); LN("THE WOLVES OVERPOWERED YOU"); injury = 1;
                if (!checkIllness()) postEvent();
            } else {
                if (sc <= 2) LN("NICE SHOOTIN' PARDNER---THEY DIDN'T GET MUCH");
                else LN("SLOW ON THE DRAW---THEY GOT AT YOUR FOOD AND CLOTHES");
                bullets -= 20 * (double)sc; cloth -= (double)sc * 4; food -= (double)sc * 8;
                postEvent();
            }
        }
        return;
    }
    if (st == EAT){
        double v;
        if (!pyfloat(line, len, &v)){ LN("PLEASE ENTER A NUMBER"); S("? "); return; }
        if (v < 1 || v > 3){ LN(v < 1 ? "NOT ENOUGH" : "TOO MUCH"); S("? "); return; }
        i64 e = T(v); double fc = 8 + 5 * (double)e;
        if (food >= fc){
            food -= fc; eat = (int)e;
            mile += 200 + (oxen - 220) / 3 + 10 * rnd();
            int r = randomEvent();
            if (r == 0) postEvent();
        } else { LN("YOU CAN'T EAT THAT WELL"); S("? "); }
        return;
    }
    if (st == FMIN || st == FFAN || st == FKIN){
        int yes = ieq(line, len, "YES"), no = ieq(line, len, "NO");
        if (!yes && !no){
            LN("PLEASE ANSWER YES OR NO");
            S(st == FMIN ? "WOULD YOU LIKE A MINISTER? " : st == FFAN ? "WOULD YOU LIKE A FANCY FUNERAL? " : "WOULD YOU LIKE US TO INFORM YOUR NEXT OF KIN? ");
            return;
        }
        if (st == FMIN){ S("WOULD YOU LIKE A FANCY FUNERAL? "); st = FFAN; }
        else if (st == FFAN){ S("WOULD YOU LIKE US TO INFORM YOUR NEXT OF KIN? "); st = FKIN; }
        else {
            if (no){ LN("BUT YOUR AUNT SADIE IN ST. LOUIS IS REALLY WORRIED ABOUT YOU"); NL(); }
            else { LN("THAT WILL BE $4*50 FOR THE TELEGRAPH CHARGE."); NL(); }
            LN("WE THANK YOU FOR THIS INFORMATION AND WE ARE SORRY YOU");
            LN("DIDN'T MAKE IT TO THE GREAT TERRITORY OF OREGON");
            LN("BETTER LUCK NEXT TIME"); NL(); NL();
            SP(30); LN("SINCERELY"); NL();
            SP(17); LN("THE OREGON CITY CHAMBER OF COMMERCE");
            st = OVER; over = 1;
        }
        return;
    }
}

#ifdef NATIVE
#include <string.h>
#include <stdlib.h>
int main(int argc, char **argv){
    (void)argc;
    ot_boot((u32)strtoul(argv[1], 0, 10));
    char line[512];
    while (fgets(line, 512, stdin)){
        char *tab = strchr(line, '\t');
        if (!tab) continue;
        *tab = 0;
        double ms = strtod(line, 0);
        char *txt = tab + 1;
        int n = (int)strlen(txt);
        while (n && (txt[n-1] == '\n' || txt[n-1] == '\r')) n--;
        if (over){ fprintf(stderr, "input left over after game end\n"); return 1; }
        js_print(txt, n); js_print("\n", 1);
        memcpy(inbuf, txt, (size_t)n);
        ot_feed(n, ms);
    }
    if (!over){ fprintf(stderr, "game not over after all inputs\n"); return 1; }
    return 0;
}
#endif

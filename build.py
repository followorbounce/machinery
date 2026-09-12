#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator for the Heavy Machinery Encyclopedia.
Reads the MACHINES / CONCEPTS content specs below and emits static HTML,
plus data/graph.json (the single source of truth for nav + relationships),
sitemap.xml, robots.txt and llms.txt. No build framework required: run
`python3 build.py` from the project root any time content changes.
"""
import json, math, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://followorbounce.github.io/machinery"
BASE = "/machinery/"

CATEGORIES = [
    {"id": "construction-equipment", "label": "Construction Equipment"},
    {"id": "mining-equipment", "label": "Mining Equipment"},
    {"id": "underground-equipment", "label": "Underground Equipment"},
    {"id": "agricultural-machinery", "label": "Agricultural Machinery"},
    {"id": "forestry-machinery", "label": "Forestry Machinery"},
    {"id": "industrial-material-handling", "label": "Industrial & Material Handling"},
    {"id": "military-engineering-vehicles", "label": "Military Engineering Vehicles"},
    {"id": "special-purpose-machines", "label": "Special Purpose Machines"},
]

DOMAINS = [
    {"id": "mechanics", "label": "Mechanics"},
    {"id": "gears", "label": "Gears"},
    {"id": "hydraulics", "label": "Hydraulics"},
    {"id": "engines", "label": "Engines"},
    {"id": "clutches-transmissions", "label": "Clutches & Transmissions"},
    {"id": "power-transmission", "label": "Power Transmission"},
]

# ------------------------------------------------------------------
# CONCEPTS
# ------------------------------------------------------------------
CONCEPTS = [
    {
        "slug": "torque", "title": "Torque", "domain": "mechanics",
        "interactive": "lever-torque",
        "stats": [("Unit", "N·m (lb-ft)"), ("Also called", "Moment of force"), ("Governs", "Every rotating driveline")],
        "definition": "Torque is a twisting force — how hard something is being turned around an axis, rather than pushed in a straight line. It is the rotational equivalent of force, and it is the single number that decides whether an engine can turn a wheel, a bolt, or a bucket wheel the size of a building.",
        "principle": "Torque depends on two things: how hard you push, and how far from the pivot you push it. The same 50 kg push on a 2-metre wrench produces twice the twisting effect of the same push on a 1-metre wrench — the force hasn't changed, only its leverage has. Every gearbox, final drive, and hydraulic motor on this site exists to change that lever arm without changing the force at the source.",
        "formulas": [("Torque", "τ = F × r", "F = applied force, r = the perpendicular distance from the pivot to the line of the force (the lever arm).")],
        "facts": [
            "A diesel engine's torque, not its horsepower, is what actually gets a loaded haul truck moving from a dead stop — horsepower only matters once the truck is already rolling.",
            "Torque and power are linked by rotational speed: P = τ × ω, which is why a low-revving diesel and a high-revving turbine can produce the same power from very different torque figures.",
            "Torque wrenches exist because a bolt is really a very short, very stiff lever — over-torque it and you don't push it in further, you shear the threads.",
        ],
        "related_concepts": ["mechanical-advantage", "gear-ratios"],
    },
    {
        "slug": "mechanical-advantage", "title": "Mechanical Advantage", "domain": "mechanics",
        "interactive": "lever-ma",
        "stats": [("Formula", "MA = output / input"), ("Trade-off", "Force for distance"), ("Oldest example", "The lever, ~3000 BCE")],
        "definition": "Mechanical advantage is the factor by which a machine multiplies an input force. A machine with a mechanical advantage of 20 turns 50 kg of push into 1,000 kg of usable force — at the cost of the input having to move 20 times farther or faster than the output.",
        "principle": "No machine creates energy; mechanical advantage only trades force against distance so that work in equals work out. A dragline's rigging, a forklift's hydraulic ram, and a bulldozer's final drive are all, underneath the steel, the same three-thousand-year-old idea as a crowbar under a rock — just reapplied through wire rope, oil pressure, or gear teeth instead of a wooden pole.",
        "formulas": [("Mechanical advantage", "MA = Fout / Fin", "A hydraulic ram with 10:1 area ratio and a gear train with a 10:1 ratio give the identical multiplication — the physics doesn't care which mechanism delivers it.")],
        "facts": [
            "Archimedes is credited with the (probably apocryphal) claim that with a long enough lever and a place to stand, he could move the Earth — dimensionally, he wasn't wrong, only practically.",
            "A block-and-tackle pulley system used on cranes multiplies force by the number of rope segments supporting the load — count the strands to know the mechanical advantage.",
            "Every one of the twenty machines on this site owes at least one of its major systems to mechanical advantage: it is the most-cited concept in the whole encyclopedia.",
        ],
        "related_concepts": ["torque", "hydraulic-cylinders"],
    },
    {
        "slug": "gear-ratios", "title": "Gear Ratios", "domain": "gears",
        "interactive": "gear-ratio",
        "stats": [("Formula", "ratio = teeth(out) / teeth(in)"), ("Trades", "Speed for torque"), ("Used in", "Every geared drivetrain on this site")],
        "definition": "A gear ratio is the number of teeth on the driven gear divided by the number of teeth on the driving gear. It tells you, in one number, how a gear pair changes rotational speed and torque as power passes through it.",
        "principle": "Mesh a small gear (the pinion) into a large one, and the large gear turns slower but with proportionally more torque — the same mechanical-advantage trade-off as a lever, delivered through interlocking teeth instead of a rigid bar. Reverse the pair and you get the opposite trade: speed instead of torque. A final drive on a bulldozer might use a ratio as steep as 6:1 specifically because the tracks need overwhelming torque at walking speed, never high speed at low torque.",
        "formulas": [
            ("Gear ratio", "GR = N₂ / N₁", "N₁ = teeth on the driving gear, N₂ = teeth on the driven gear."),
            ("Speed change", "ω₂ = ω₁ / GR", "Output speed falls by exactly the same factor the ratio raises torque — energy is conserved, not created."),
        ],
        "facts": [
            "Two meshed gears always spin in opposite directions — an odd number of gears in a train restores the original direction, an even number reverses it.",
            "A gear ratio doesn't have to come from a single pair: a gearbox chains several ratios together, multiplying them, to cover a huge range from one small engine.",
            "The teeth count, not the gear's physical size, is what sets the ratio — two gears of very different diameters but the same tooth pitch and count produce a 1:1 ratio.",
        ],
        "related_concepts": ["torque", "planetary-gears"],
    },
    {
        "slug": "planetary-gears", "title": "Planetary Gears", "domain": "gears",
        "interactive": "planetary",
        "stats": [("Members", "Sun, planets, ring, carrier"), ("Advantage", "Huge ratio in a small housing"), ("Used in", "Final drives, TBM cutterheads, automatic transmissions")],
        "definition": "A planetary (epicyclic) gearset arranges a central sun gear, several orbiting planet gears on a carrier, and an outer ring gear with internal teeth, all meshed together and sharing one axis. Fixing any one of the three members and driving another produces a different gear ratio from the same set of parts.",
        "principle": "Because load is shared across three or more planet gears instead of a single meshing pair, a planetary set transmits far more torque for its size and weight than an equivalent simple gear train — which is exactly why it lives inside the tight final-drive housing at a bulldozer's track sprocket, or inside a tunnel boring machine's cutterhead drive, where space is the scarcest resource on the machine.",
        "formulas": [("Ratio, ring fixed", "GR = 1 + (N_ring / N_sun)", "Driving the sun gear with the ring gear held stationary is the most common configuration in heavy-equipment final drives.")],
        "facts": [
            "The same physical planetary gearset can produce several different ratios just by changing which member is held stationary — this is exactly how a planetary automatic transmission shifts gears without a clutch pedal.",
            "Because the planet gears orbit the sun gear the same way moons orbit a planet, the arrangement borrowed its name directly from astronomy.",
            "A single-stage planetary set can realistically achieve ratios up to about 10:1; stacking two or three stages in series reaches into the hundreds, which is exactly what a large final drive needs.",
        ],
        "related_concepts": ["gear-ratios", "final-drives-differentials"],
    },
    {
        "slug": "pascals-law", "title": "Pascal's Law", "domain": "hydraulics",
        "interactive": "hydraulic-force",
        "stats": [("Formulated by", "Blaise Pascal, 1653"), ("States", "Pressure transmits equally"), ("Powers", "Every hydraulic machine on this site")],
        "definition": "Pascal's Law states that pressure applied to a confined, incompressible fluid is transmitted equally, undiminished, in every direction throughout that fluid. It is the entire physical basis of hydraulic machinery.",
        "principle": "Because pressure is force divided by area, the same pressure acting on a large piston produces far more force than it does acting on a small one. Push a small piston with a modest force and connect it through oil to a much larger piston, and the large piston pushes back with a proportionally larger force — trading distance for force exactly the way a lever does, except the 'lever arm' here is a ratio of areas, and the force can be redirected anywhere a hose can reach.",
        "formulas": [
            ("Pascal's Law", "P = F / A", "Pressure is uniform throughout a connected, static fluid."),
            ("Force multiplication", "F₂ = F₁ × (A₂ / A₁)", "A₁, A₂ = the areas of the input and output pistons. This is the master equation behind every hydraulic cylinder on this site."),
        ],
        "facts": [
            "A car's hydraulic brakes are a direct, everyday application of the same law that lets a 40-tonne excavator curl its bucket: a small pedal piston, a much larger caliper piston.",
            "Hydraulic fluid is treated as incompressible for these calculations — it isn't perfectly so, but the compression is small enough at working pressures to ignore for engineering purposes.",
            "Because pressure, not force, is what's constant throughout the system, the same hydraulic pump can drive a small, fast cylinder and a huge, slow one simultaneously, just by giving them different piston areas.",
        ],
        "related_concepts": ["hydraulic-cylinders", "mechanical-advantage"],
    },
    {
        "slug": "hydraulic-cylinders", "title": "Hydraulic Cylinders", "domain": "hydraulics",
        "interactive": "cylinder-flow",
        "stats": [("Type", "Linear actuator"), ("Typical pressure", "200 – 350 bar in heavy equipment"), ("Found in", "Booms, buckets, blades, outriggers")],
        "definition": "A hydraulic cylinder is a tube, a piston, and a rod that turns fluid pressure directly into a straight-line push or pull. It is the most common actuator on any heavy machine built after about 1950, because it can deliver enormous force from a compact, sealed package with no gears at all.",
        "principle": "Pump oil into one side of the piston and it pushes the rod out; pump oil into the other side and it pulls the rod back in — the direction is controlled entirely by a valve, not by the cylinder itself. Because force scales with piston area (Pascal's Law), a boom cylinder only a few hundred millimetres across can lift many tonnes at the far end of an excavator's arm, at working pressures that would be lethal if the seals ever failed.",
        "formulas": [("Cylinder force", "F = P × A = P × π(d/2)²", "d = the piston's bore diameter. Doubling the bore quadruples the force from the same pressure.")],
        "facts": [
            "A double-acting cylinder — pressurised on both sides in turn — can push and pull with force; a single-acting cylinder can only push, and relies on gravity or a spring to retract.",
            "The 'stick' cylinder on a large excavator can be over a metre in bore diameter, built more like a piece of pressure-vessel engineering than a typical mechanical part.",
            "Cylinder seals, not the steel tube, are usually the first thing to wear out on a hydraulic machine — a scored rod as thin as a human hair can leak enough to stall a boom mid-lift.",
        ],
        "related_concepts": ["pascals-law", "mechanical-advantage"],
    },
    {
        "slug": "four-stroke-diesel-cycle", "title": "Four-Stroke Diesel Cycle", "domain": "engines",
        "interactive": "four-stroke",
        "stats": [("Strokes per cycle", "4"), ("Ignition", "Compression, no spark plug"), ("Typical compression ratio", "14:1 to 22:1")],
        "definition": "The four-stroke diesel cycle is the sequence of intake, compression, power, and exhaust that a diesel engine's piston repeats to convert fuel into rotating torque. Unlike a petrol engine, it ignites fuel using heat from compression alone, with no spark plug.",
        "principle": "On the intake stroke the piston draws in only air. On compression, that air is squeezed hard enough — often 14 to 22 times smaller — that its temperature alone exceeds diesel fuel's ignition point. Fuel is injected right at that moment and ignites immediately on contact with the superheated air, driving the piston down on the power stroke; the exhaust stroke then clears the cylinder for the next cycle. Every crankshaft revolution moves the piston through two strokes, so a four-stroke engine fires each cylinder once every two revolutions.",
        "formulas": [("Compression ratio", "CR = (Vd + Vc) / Vc", "Vd = swept (displacement) volume, Vc = clearance volume remaining at top dead centre. Higher CR means hotter compressed air and easier diesel ignition.")],
        "facts": [
            "Because diesel ignition needs no spark, diesel engines can run at far higher compression than petrol engines — one reason they extract more work from the same fuel energy.",
            "Turbocharging (see Chapter link below) exists largely to fix diesel's one weakness at altitude and low RPM: not enough air packed into the cylinder to burn the fuel completely.",
            "The largest mining haul trucks run two of these engines' industrial cousins side by side, purely because no single diesel yet built is compact enough to deliver the combined output alone.",
        ],
        "related_concepts": ["torque", "torque-converters"],
    },
    {
        "slug": "torque-converters", "title": "Torque Converters", "domain": "clutches-transmissions",
        "interactive": "torque-converter",
        "stats": [("Type", "Fluid coupling"), ("Multiplies torque", "Up to ~2:1 at stall"), ("Used in", "Automatic transmissions, dozers, wheel loaders")],
        "definition": "A torque converter connects an engine to a transmission with spinning fluid instead of a mechanical clutch plate. It transmits power smoothly through oil, and — unlike a simple fluid coupling — can actually multiply torque when the engine is spinning much faster than the output shaft.",
        "principle": "Inside its sealed housing, an engine-driven impeller flings transmission fluid outward into a connected turbine, which drives the output shaft; a third element, the stator, redirects the returning fluid to add rather than fight the impeller's flow. That redirection is what lets a stalled torque converter — output shaft barely turning, as at the start of a dozer push — deliver up to roughly twice the engine's torque to the tracks, tapering back to a 1:1 fluid coupling once both sides spin near the same speed.",
        "formulas": [("Torque multiplication ratio", "TR = τ_out / τ_in", "Maximum near stall (large speed difference between impeller and turbine), falling to about 1:1 once impeller and turbine speeds converge.")],
        "facts": [
            "A torque converter is why a heavy machine in gear can sit still against the brake with the engine revving and not stall — there is no rigid mechanical link to lock up.",
            "The fluid coupling inside runs hot enough under sustained heavy load that it needs its own dedicated oil cooler, often larger than the engine's coolant radiator.",
            "Many modern torque converters include a lock-up clutch that bolts the impeller directly to the turbine once they're spinning together, trading the converter's smoothness for a mechanical connection's efficiency.",
        ],
        "related_concepts": ["gear-ratios", "final-drives-differentials"],
    },
    {
        "slug": "final-drives-differentials", "title": "Final Drives & Differentials", "domain": "power-transmission",
        "interactive": "final-drive",
        "stats": [("Location", "Last stage before the wheels/tracks"), ("Typical ratio", "4:1 to 40:1 depending on machine"), ("Differential's job", "Allow left/right speed difference")],
        "definition": "The final drive is the last gear reduction in a driveline, sitting right at the wheel hub or track sprocket, where the very highest torque and lowest speed in the whole machine are required. The differential, usually just upstream of it, allows the two output shafts to spin at different speeds — essential the moment the machine turns a corner.",
        "principle": "An engine spins fast but with comparatively little torque; a final drive's job is to spend the last, steepest gear reduction of the whole driveline turning that speed into torque, right where the ground finally meets the machine. A differential solves a problem final drives alone can't: in a turn, an outside wheel or track must travel farther, and therefore faster, than the inside one, so the differential splits incoming torque between two output shafts while letting them rotate independently — normally, at the cost of always sending more torque to whichever wheel spins easiest, which is why heavy machines add lockable or limited-slip differentials for low-traction ground.",
        "formulas": [("Overall drive ratio", "GR_total = GR_transmission × GR_final drive", "The final drive typically supplies the single largest reduction of the two — often steeper than every transmission gear combined.")],
        "facts": [
            "A locked differential sends equal torque to both sides regardless of traction — essential in mud or on a slope, but it fights the machine on a hard-surfaced turn and is disengaged as soon as traction allows.",
            "Tracked machines like bulldozers and excavators don't use a differential in the wheeled sense at all — each track has its own final drive, and steering comes from slowing or reversing one side.",
            "A final drive failure is one of the most expensive repairs on a mining haul truck, because the whole reduction gearset sits sealed inside the wheel hub, submerged in gear oil, exactly where dirt and heat both concentrate.",
        ],
        "related_concepts": ["gear-ratios", "torque"],
    },
    {
        "slug": "bearings", "title": "Bearings", "domain": "power-transmission",
        "interactive": "bearing-cutaway",
        "stats": [("Job", "Let parts rotate with minimum friction"), ("Main types", "Ball, roller, plain, slew"), ("Failure mode", "Contamination, most often"), ],
        "definition": "A bearing is the part of a machine designed to take the friction, so nothing more expensive around it has to. It supports a rotating or sliding component while letting it move with as little resistance and wear as possible.",
        "principle": "Two hard steel surfaces sliding directly against each other under load generate heat and wear at a rate no machine could survive in continuous service — a bearing interrupts that direct contact, either with a layer of rolling balls or rollers (rolling-element bearings) or with a thin, continuously replenished film of oil (plain/journal bearings) that keeps the two surfaces from ever quite touching. A slew bearing, the giant ring gear a whole excavator's upper structure rotates on, is really just this same idea scaled up to a component several metres across.",
        "formulas": [("Basic friction relation", "F_friction = μ × N", "μ = coefficient of friction, N = normal load. A good rolling-element bearing can cut effective μ by a factor of ten or more compared to unlubricated sliding contact.")],
        "facts": [
            "The slew ring under a large excavator's cab can be several metres in diameter, carry the machine's entire upper weight, and still needs to rotate smoothly enough for fine bucket control.",
            "Bearing contamination — a single grain of grit in the wrong place — is the single most common cause of premature bearing failure in heavy equipment, ahead of pure overload.",
            "Fluid (journal) bearings, used in large engine crankshafts, never let metal touch metal at all in normal operation — they ride on a wedge of pressurised oil only a few hundredths of a millimetre thick.",
        ],
        "related_concepts": ["torque", "final-drives-differentials"],
    },
]

# ------------------------------------------------------------------
# MACHINES
# ------------------------------------------------------------------
MACHINES = [
    {
        "slug": "liebherr-r9800", "title": "Liebherr R 9800", "category": "mining-equipment",
        "summary": "An 800-tonne hydraulic mining excavator built to load the very largest haul trucks in a handful of passes, and one of the two or three largest hydraulic excavators ever put into series production.",
        "purpose": "It exists to close the gap between hydraulic excavators and the largest cable shovels — giving mines a hydraulic machine that can still load the biggest haul trucks in a handful of passes, without switching to cable-and-hoist mechanics.",
        "scale": (10.34, "transport height"),
        "stats": [("Operating weight", "800 t"), ("Bucket capacity", "up to 42 m³"), ("Engine power", "4,000 hp"), ("Configuration", "Backhoe or face shovel")],
        "history": "Liebherr introduced the R 9800 in 2011 to compete directly with cable-operated electric mining shovels on the biggest jobs, betting that hydraulics — by then dominant at every smaller size class — could scale all the way to the top of the market. It has since become a fixture at copper and oil-sands operations that need a shovel able to fill a 400-tonne haul truck in three to five passes.",
        "components": [
            ("Undercarriage", "Twin-crawler base carrying the full 800-tonne weight and distributing it across the ground at a pressure the pit floor can actually support."),
            ("Slew ring & house", "The turntable bearing and upper structure that let the entire cab, boom, and counterweight rotate independently of the tracks."),
            ("Boom & stick (or dipper handle)", "The two-piece arm — configurable as a backhoe or a face shovel — that positions the bucket."),
            ("Hydraulic cylinders", "Boom, stick, and bucket cylinders, some over a metre in bore diameter, that do all the digging force work."),
            ("Twin diesel engines", "Two engines running in parallel, because no single diesel built reaches 4,000 hp in a package this size."),
        ],
        "how_it_works": "Two diesel engines drive a bank of hydraulic pumps that pressurise oil to roughly 350 bar. Operator inputs open proportional valves that route that pressurised oil to the boom, stick, and bucket cylinders in whatever combination curls the bucket through the bank, exactly like a human arm scaled up a hundredfold. The same hydraulic system also drives the crawler tracks and the slew motor that rotates the whole upper structure to dump each load into a waiting truck.",
        "principles": [
            ("hydraulic-cylinders", "Every digging motion — boom, stick, and bucket curl — is a hydraulic cylinder converting oil pressure directly into linear force at a scale few other machines approach."),
            ("pascals-law", "The whole hydraulic system is Pascal's Law in industrial form: one pressure, generated once, delivered wherever a hose can reach."),
            ("torque", "The slew drive that rotates the 800-tonne upper structure needs sustained torque, not speed, to start and stop that mass smoothly."),
        ],
        "performance": [("Operating weight", "800 t (backhoe)"), ("Bucket capacity", "36 – 42 m³"), ("Engine output", "2 × 2,000 hp"), ("Max digging depth", "~9 m"), ("Max tear-out force", "1,760 kN")],
        "examples": [("R 9800 fleet, Chilean copper mines", "Multiple units run in tandem with Cat 797-class haul trucks at some of the world's largest open-pit copper operations."), ("Athabasca oil sands, Canada", "R 9800s in face-shovel configuration load oil-sands ore directly into haul trucks ahead of processing.")],
        "facts": [
            "Its standard bucket, at up to 42 m³, could comfortably hold a small delivery van.",
            "The R 9800 can be configured on-site as either a backhoe (digging toward itself) or a face shovel (digging upward and away) by rearranging the same boom components.",
            "At 800 tonnes, it weighs roughly as much as a fully loaded Airbus A380.",
        ],
    },
    {
        "slug": "caterpillar-d11", "title": "Caterpillar D11", "category": "construction-equipment",
        "summary": "Caterpillar's largest production bulldozer, built to push more material per pass than any other dozer in its catalogue, almost exclusively in mining rather than general construction.",
        "purpose": "Built for one job only: moving more material per dozer pass than anything else in Caterpillar's catalogue, on ground too demanding for a mid-size dozer to clear economically.",
        "scale": (4.5, "overall height, top of exhaust stack"),
        "stats": [("Operating weight", "112.7 t"), ("Flywheel power", "850 hp"), ("Blade capacity", "43.6 m³"), ("Engine", "Cat C32 ACERT")],
        "history": "The D11 lineage traces back to Caterpillar's push through the 1980s and 1990s to build ever-larger track-type tractors for surface mining, where a single dozer pass moving more material directly cuts cost per tonne. Successive D11 generations (D11N, D11R, D11T, and today's D11) have kept the same basic architecture — single engine, single blade, elevated sprocket drive — while steadily raising weight and horsepower.",
        "components": [
            ("Elevated sprocket final drive", "Keeps the drive sprocket up and away from ground-level impact loads, protecting it from the abuse a mining dozer takes daily."),
            ("Semi-U or U-blade", "A blade profile chosen for holding more material in front of the dozer without spilling over the sides."),
            ("Torque converter & powershift transmission", "Delivers smooth, stallable power straight to the tracks, exactly what a dozer needs when it hits an immovable pile mid-push."),
            ("Ripper (optional rear attachment)", "A single or multi-shank ripper that can tear up rock too hard to push directly, ahead of a following blade pass."),
        ],
        "how_it_works": "The C32 diesel drives a torque converter, which multiplies torque further at the moment the blade meets real resistance — exactly when a stalled or slow-moving dozer needs it most. That torque then passes through a planetary powershift transmission and steering system into the final drives at each track sprocket, the last and steepest gear reduction in the chain, which is what actually lets 850 engine horsepower become enough drawbar pull to shove tens of tonnes of rock.",
        "principles": [
            ("torque-converters", "The torque converter is what lets the D11 stall against an immovable pile without killing the engine, then recover smoothly as the load eases."),
            ("final-drives-differentials", "Each track's final drive supplies the last, steepest torque multiplication, turning modest track speed into overwhelming pushing force."),
            ("mechanical-advantage", "A dozer blade is, in the end, a lever pushing horizontally — its whole geometry is chosen to maximise usable pushing force for a given engine output."),
        ],
        "performance": [("Operating weight", "112.7 t"), ("Flywheel power", "850 hp (630 kW)"), ("Blade capacity (U-blade)", "43.6 m³"), ("Length", "10.9 m"), ("Blade width", "6.7 m")],
        "examples": [("Oil sands overburden stripping, Alberta", "D11s work in tandem lines clearing overburden ahead of shovel-and-truck fleets."), ("Coal mine reclamation sites", "Large dozers like the D11 regrade spoil piles back toward natural contours after mining ends.")],
        "facts": [
            "Its blade alone can hold enough material to fill roughly four standard highway dump trucks in one push.",
            "The elevated sprocket design, distinctive on every large Caterpillar dozer since the D9H, keeps the final drive completely clear of the ground, sparing it the impact loads a low-mounted sprocket would absorb.",
            "A D11 costs more, new, than most single-family homes — and mining operations routinely run several at once.",
        ],
    },
    {
        "slug": "caterpillar-994k", "title": "Caterpillar 994K", "category": "construction-equipment",
        "summary": "Caterpillar's largest wheel loader, built to load haul trucks directly rather than push or carry material any real distance — a specialist at one job, done at enormous scale.",
        "purpose": "Exists purely to keep the largest haul trucks fed — a wheel loader sized specifically to fill a 150 – 300 t truck in three to five passes, nothing more.",
        "scale": (7.1, "overall height, ground to top of ROPS"),
        "stats": [("Operating weight", "~243 t"), ("Engine power", "1,739 hp"), ("Bucket capacity", "19 – 24.5 m³"), ("Loading targets", "150 – 300 t haul trucks")],
        "history": "Wheel loaders scaled up alongside haul trucks through the late 20th century, because a loader too small for its truck fleet becomes the bottleneck at every load cycle. The 994 series has been Caterpillar's answer at the top end of that race since the 1990s, growing through the 994D, 994F, and 994H before the current 994K, matched specifically to load the largest Cat mining trucks in three to five bucket passes.",
        "components": [
            ("Z-bar loader linkage", "The geometry connecting the lift arms, bucket, and hydraulic cylinders, chosen to maximise breakout force through the bucket's whole lifting arc."),
            ("Articulated frame joint", "Lets the entire front half of the machine pivot relative to the rear for tight-radius steering despite the loader's enormous wheelbase."),
            ("Twin hydraulic pump system", "Separate circuits for lift and tilt functions, sized to move tens of tonnes of material per cycle without the boom and bucket fighting each other for flow."),
            ("Torque-converter powershift drivetrain", "Delivers the smooth, stallable power a loader needs when its bucket bites into an unmoved pile."),
        ],
        "how_it_works": "The operator drives the bucket into the pile, curling it via a hydraulic cylinder acting through the Z-bar linkage to maximise breakout force at the cutting edge. A second set of cylinders then lifts the loaded bucket, and the whole articulated machine reverses, turns via its centre-frame hinge, and dumps directly into a haul truck's bed positioned alongside. The cycle — dig, lift, swing, dump, return — repeats until the truck reaches its rated payload, typically in three to five passes for a matched 994K-and-haul-truck pairing.",
        "principles": [
            ("hydraulic-cylinders", "Lift and tilt cylinders, driven by twin pump circuits, do essentially all of the loader's useful work."),
            ("torque-converters", "The torque-converter drivetrain lets the 994K stall its wheels against a pile without stalling the engine, exactly as a dozer does."),
            ("mechanical-advantage", "The Z-bar linkage geometry is tuned specifically to trade lift-arm speed for maximum breakout force right at the bucket edge, where digging resistance is highest."),
        ],
        "performance": [("Operating weight", "~243 t"), ("Engine power", "1,739 hp (1,297 kW)"), ("Bucket capacity", "19.1 – 24.5 m³"), ("Bucket width", "6.24 m"), ("Travel speed", "24.5 km/h")],
        "examples": [("Copper and iron-ore open pits worldwide", "994K units are matched almost exclusively to 150–300 t haul truck fleets at the largest surface mines."), ("Oil sands mining, Canada", "Used to load oil-sands ore where shovels aren't already positioned for the job.")],
        "facts": [
            "A single bucket load can exceed 30 tonnes of dense ore — heavier than most entire mid-size dozers.",
            "The 994K is deliberately not used for general carrying or dozing; at this size, driving material any real distance wastes the machine's whole reason for existing.",
            "Its tyres alone, sized for this weight class, can each cost more than a typical passenger car.",
        ],
    },
    {
        "slug": "caterpillar-24m", "title": "Caterpillar 24 Motor Grader", "category": "construction-equipment",
        "summary": "The largest motor grader Caterpillar builds, sized specifically to maintain the wide haul roads inside a mine rather than the narrower roads a construction grader typically finishes.",
        "purpose": "Exists to keep haul roads within the tight tolerance mine-truck tyres depend on — a job that pays for the machine's size many times over in extended tyre life alone.",
        "scale": (4.45, "overall height, top of cab"),
        "stats": [("Operating weight", "~65.8 t"), ("Blade length", "24 ft class"), ("Role", "Mine haul-road maintenance"), ("Wheel configuration", "6×4 or 6×6")],
        "history": "Motor graders scaled up specifically to keep pace with the haul roads mining trucks depend on: a rutted or poorly cambered haul road wears tyres and suspension components on every truck that crosses it, all day, so a grader capable of maintaining a very wide road in fewer passes pays for its size many times over. Caterpillar's 24-class graders have occupied the top of that size range for decades.",
        "components": [
            ("Long wheelbase frame", "Stretched well beyond a construction grader's frame to keep the blade stable and the cut accurate across a wide haul road."),
            ("Circle & drawbar", "The rotating ring beneath the frame that lets the blade angle, tilt, and sideshift independently of the machine's direction of travel."),
            ("Moldboard (blade)", "A blade roughly 24 feet long, the machine's namesake, that shapes and smooths the road surface in a single pass."),
            ("Articulated or rigid frame steering", "Allows precise, repeatable steering control critical to maintaining a consistent road crown."),
        ],
        "how_it_works": "Hydraulic cylinders rotate the circle beneath the frame to set the blade's angle relative to the direction of travel, then tilt and raise or lower it to the cutting depth the operator wants. As the grader moves forward, the angled blade shears off high spots and redistributes material into low spots and the road's crown, restoring the smooth, correctly cambered surface that keeps water shedding off the road instead of pooling and softening it.",
        "principles": [
            ("gear-ratios", "The powershift transmission's gear steps are tuned for the narrow, steady speed range grading actually requires, unlike a haul truck's broad speed range."),
            ("hydraulic-cylinders", "Every blade movement — angle, tilt, sideshift, lift — is driven by a dedicated hydraulic cylinder acting on the circle and drawbar."),
            ("bearings", "The circle itself rides on a large-diameter bearing race that has to stay precise under constant vibration and dust for the blade angle to hold true."),
        ],
        "performance": [("Operating weight", "~65.8 t"), ("Blade length", "24 ft (7.3 m)"), ("Wheelbase", "~7.9 m"), ("Typical role", "Mine haul-road maintenance")],
        "examples": [("Major open-pit haul road networks worldwide", "24M-class graders run scheduled maintenance passes to keep haul roads within the tight tolerances mine-truck tyre life depends on.")],
        "facts": [
            "A well-maintained haul road can double the useful tyre life of every truck that runs on it — which is why a mine will run a grader this large purely on road upkeep, never digging anything itself.",
            "Its blade can shift, tilt, and angle independently, letting one pass both cut a crown and cast material toward the road's edge.",
            "Despite its size, fine control is the point: a grader operator is expected to hold the blade within centimetres of a target grade all day.",
        ],
    },
    {
        "slug": "caterpillar-797f", "title": "Caterpillar 797F", "category": "mining-equipment",
        "summary": "The largest mechanical-drive haul truck Caterpillar builds — a 400-ton-payload truck powered by a single, enormous diesel engine rather than the diesel-electric drivetrains some rivals use at this size.",
        "purpose": "Built to move the maximum payload a single mechanical drivetrain can handle, so a mine can haul more ore per truck without switching to a diesel-electric design.",
        "scale": (7.44, "overall height, top of ROPS (empty)"),
        "stats": [("Payload capacity", "400 short tons"), ("Engine", "Cat C175-20, 4,000 hp"), ("Drive type", "Mechanical (torque converter + gearbox)"), ("Tyres", "6, at roughly 4 m diameter each")],
        "history": "Caterpillar introduced the original 797 in 1998 specifically to compete at the top of the ultra-class haul truck market with a mechanical drivetrain, at a time when many rivals of similar size used diesel-electric drive. Successive versions — 797, 797B, and today's 797F — have kept that mechanical-drive bet while steadily raising engine output, culminating in the C175-20's 4,000 hp, about 450 hp more than its predecessor.",
        "components": [
            ("Cat C175-20 engine", "A 20-cylinder, quad-turbocharged diesel displacing 106 litres — the core reason this truck can move at all."),
            ("Torque converter & powershift transmission", "Caterpillar's mechanical alternative to a diesel-electric drivetrain, chosen for serviceability and efficiency across the truck's full speed range."),
            ("Final drives", "Massive planetary reduction units at each rear wheel hub, delivering the last and steepest torque multiplication before the tyres."),
            ("Dump body", "A reinforced steel bed engineered to survive a 400-ton payload of blasted rock being dropped into it, truck after truck, for years."),
        ],
        "how_it_works": "The C175-20 engine drives a torque converter and powershift transmission — the same basic chain as a bulldozer's, scaled up — through to final drives at the rear wheel hubs. Those final drives supply the last, steepest gear reduction, turning the engine's speed into the torque needed to move a fully loaded 620-plus-tonne gross weight up a mine's ramp grades, typically limited to around 10 percent specifically so trucks like this one can climb them loaded.",
        "principles": [
            ("torque", "Torque, not top speed, is what actually gets 400 tons of payload moving up a haul-road grade from a stop."),
            ("final-drives-differentials", "The rear final drives deliver the last and largest torque multiplication in the whole driveline, right at the wheel hub."),
            ("four-stroke-diesel-cycle", "The C175-20's twenty cylinders each run the same basic four-stroke diesel cycle as a small generator engine, just twenty times over and turbocharged four times."),
        ],
        "performance": [("Payload capacity", "400 short tons (363 t)"), ("Gross machine weight", "~624 t loaded"), ("Engine power", "4,000 hp (2,983 kW)"), ("Engine displacement", "106 L"), ("Top speed (loaded)", "~68 km/h")],
        "examples": [("Escondida copper mine, Chile", "One of the world's largest copper operations runs large fleets of ultra-class haul trucks in this size class."), ("Athabasca oil sands, Canada", "797-class trucks haul oil-sands ore from shovel to processing across some of the industry's longest in-pit haul routes.")],
        "facts": [
            "Its six tyres, at roughly 4 metres in diameter, are taller than most adult humans standing on each other's shoulders.",
            "The world's single largest haul truck by payload is actually the electric-drive BelAZ 75710, rated at 450 tonnes — the 797F remains the largest truck built around a purely mechanical drivetrain.",
            "A fully loaded 797F weighs more than a Boeing 737, moving under its own power on a dirt road.",
        ],
    },
    {
        "slug": "big-muskie-dragline", "title": "Bucyrus-Erie 4250-W “Big Muskie”", "category": "mining-equipment",
        "summary": "The largest walking dragline ever built — a single, one-off machine so large it needed its own specially built rail cars just to ship its components to the mine where it was assembled.",
        "purpose": "Purpose-built for one site: stripping Ohio coal overburden faster than any smaller dragline could, at a scale no other machine of its kind has matched before or since.",
        "scale": (68, "overall standing height (the boom itself reached about 94 m)"),
        "stats": [("Bucket capacity", "220 cubic yards (170 m³)"), ("Boom length", "310 ft (94 m)"), ("Weight", "~13,000 t"), ("Status", "Retired 1991, partly preserved")],
        "history": "Bucyrus-Erie built the 4250-W, nicknamed Big Muskie, in 1969 for the Central Ohio Coal Company, as the single largest walking dragline the company ever produced and the only one of its exact model built. It worked Ohio coal country for over two decades before rising sulphur-regulation costs and reclamation-law changes made it uneconomical, and it was retired in 1991; only its bucket survives today, preserved as a monument.",
        "components": [
            ("Boom", "A 310-foot lattice-steel boom from which the entire dragline bucket rig was suspended and swung."),
            ("Bucket and dragline rigging", "A 220-cubic-yard bucket dragged across the ground by a hoist-and-drag wire-rope system, rather than pushed like an excavator's."),
            ("Walking mechanism", "Enormous hydraulically actuated 'shoes' that let the entire machine lift itself and shuffle forward without conventional tracks or wheels."),
            ("Electric hoist and drag motors", "Powered from an external high-voltage supply rather than an onboard engine — dragines of this size are electric, not diesel, machines."),
        ],
        "how_it_works": "Big Muskie's operator swung the boom out over the material to be moved, then let the bucket fall and drag backward across the surface via the drag rope, scooping overburden into the bucket using the bucket's own weight and the drag motors' pull rather than any digging cylinder. The loaded bucket was then hoisted clear, the whole upper structure slewed around, and the load dumped onto a spoil pile — the same basic cycle every dragline in the world still uses, just at a scale no other machine has matched.",
        "principles": [
            ("mechanical-advantage", "The drag and hoist rigging is a wire-rope mechanical-advantage system, multiplying motor force through multiple rope falls exactly as a block and tackle does."),
            ("torque", "The hoist and drag motors needed sustained, enormous torque, not speed, to move a 220-cubic-yard bucket and its load through the drag cycle."),
            ("bearings", "The machine's entire upper works rotated on a slew ring bearing sized for a rotating mass in the thousands of tonnes — one of the largest bearings ever built for a mobile machine."),
        ],
        "performance": [("Bucket capacity", "220 yd³ (170 m³ / ~295 t of material)"), ("Boom length", "310 ft (94 m)"), ("Operating weight", "~13,000 t"), ("Power source", "External electric supply")],
        "examples": [("Central Ohio Coal Company operations", "Big Muskie's entire working life was spent removing overburden at a single coal complex in Ohio."), ("Its bucket, Miner's Memorial Park, Ohio", "The only surviving component, preserved as a public monument after the rest of the machine was scrapped.")],
        "facts": [
            "It was too large to move on public roads in one piece — its components arrived on specially built rail cars and it was assembled on site.",
            "A single bucket load, at 220 cubic yards, could have buried a small house.",
            "\"Walking\" draglines like this one move by lifting their whole base on giant shoes and shuffling forward a few feet at a time — they have no wheels or tracks at all.",
        ],
    },
    {
        "slug": "bagger-293", "title": "TAKRAF Bagger 293", "category": "mining-equipment",
        "summary": "A bucket wheel excavator recognised by Guinness World Records as the heaviest land vehicle ever built, and — tied with its near-sister Bagger 288 — the tallest.",
        "purpose": "Exists to strip overburden continuously, fast enough to keep pace with round-the-clock lignite extraction at a single German mine — a job cyclic excavators couldn't match.",
        "scale": (96, "height"),
        "stats": [("Length", "225 m"), ("Height", "96 m"), ("Weight", "14,200 t"), ("Bucket wheel diameter", "21.3 m, 18 buckets")],
        "history": "TAKRAF built Bagger 293 in Germany in 1995 as an evolution of the earlier Bagger 288, purpose-built to strip overburden fast enough to keep pace with coal extraction at the Hambach open-pit lignite mine. Both machines were designed around the same core insight: continuous bucket-wheel excavation moves far more material per hour than any cyclic (dig-swing-dump) excavator, at the cost of a machine so large it can only ever work one pit.",
        "components": [
            ("Bucket wheel", "A rotating wheel over 21 metres across carrying 18 buckets, each able to hold over 15 cubic metres of material."),
            ("Boom conveyor", "A belt conveyor running the length of the bucket-wheel boom, carrying excavated material back toward the machine's main body."),
            ("Crawler undercarriage", "Twelve separate crawler tracks spreading the machine's 14,200-tonne weight across a wide enough footprint to avoid sinking into the pit floor."),
            ("Counterweight boom", "A boom on the opposite side of the machine from the bucket wheel, balancing its enormous overhung weight."),
        ],
        "how_it_works": "Electric motors spin the bucket wheel continuously while the whole boom slowly swings sideways, letting each bucket scoop a shallow cut of material as it passes through the working face. Excavated material drops from each bucket onto the boom's internal conveyor the moment it clears the face, is carried back across the machine's body, and transferred onto a connecting conveyor system that can move overburden kilometres away without a single truck ever being loaded.",
        "principles": [
            ("torque", "The bucket wheel's drive motors run continuously against the resistance of cutting into a working face, needing sustained torque rather than a single peak force."),
            ("gear-ratios", "The wheel's drive train gears the electric motors' high running speed down to the wheel's much slower, high-torque cutting speed."),
            ("bearings", "Every one of its twelve crawler tracks and the bucket wheel's own axle depend on bearings rated for a static load in the thousands of tonnes."),
        ],
        "performance": [("Overall length", "225 m"), ("Height", "96 m"), ("Weight", "14,200 t"), ("Bucket wheel diameter", "21.3 m"), ("External power requirement", "16.56 MW")],
        "examples": [("Hambach surface mine, Germany", "Bagger 293 has worked continuously at this single lignite mine since 1995, stripping overburden ahead of coal extraction.")],
        "facts": [
            "At over 31 million pounds, Guinness World Records lists it as the heaviest land vehicle ever built.",
            "It moves on twelve separate crawler tracks — most excavators, however large, use only two.",
            "It draws 16.56 megawatts of external electric power, roughly enough to supply a small town, delivered continuously through cable rather than generated on board.",
        ],
    },
    {
        "slug": "komatsu-4100xpc", "title": "Komatsu P&H 4100XPC", "category": "mining-equipment",
        "summary": "An ultra-class electric rope shovel purpose-built to load the very largest mining haul trucks, using cable and hoist mechanics that predate hydraulic excavators by decades.",
        "purpose": "Built to load the very largest haul trucks in the fewest possible passes, using cable-and-hoist mechanics because, at this scale, rope still out-lifts hydraulics.",
        "scale": (10.2, "approximate — dumping height with door open; no full overall-height spec found"),
        "stats": [("Dipper capacity", "58 – 68 m³"), ("Nominal payload", "~109 t per pass"), ("Drive", "AC electric"), ("Loads trucks up to", "363 t")],
        "history": "The P&H rope-shovel line, now built under Komatsu after its acquisition of P&H Mining, descends from cable shovel designs that predate hydraulic excavators entirely — cable and hoist rigging scales to enormous sizes more readily than hydraulic cylinders do, which is exactly why the largest shovels in the world are still rope shovels rather than hydraulic ones. The 4100XPC sits at the top of that lineage, engineered specifically around loading modern ultra-class haul trucks in as few passes as possible.",
        "components": [
            ("Dipper (bucket)", "A twin-leg-handle dipper design that lets the bucket both crowd forward and hoist upward independently, rather than moving on a single fixed arc."),
            ("Hoist rope and drum", "Wire rope wound on a powerful drum that lifts the loaded dipper — the shovel's primary digging force."),
            ("Crowd mechanism", "A separate drive that pushes the dipper handle forward into the bank as the hoist rope lifts, combining the two motions into a single digging arc."),
            ("AC electric drive system", "Modern AC motors replacing the DC systems older rope shovels relied on, for finer control and lower maintenance."),
        ],
        "how_it_works": "The crowd mechanism pushes the dipper handle forward into the bank face while the hoist drum simultaneously winds in wire rope, lifting the dipper up through the material in a combined digging arc that fills the bucket using hoist tension rather than hydraulic ram force. Once full, the whole upper structure — dipper, handle, and boom — slews around on the shovel's base to swing the load over a waiting haul truck, where the dipper's door releases the load, before the cycle reverses to return for the next pass.",
        "principles": [
            ("mechanical-advantage", "The hoist rope-and-drum system is a direct wire-rope mechanical-advantage mechanism, exactly like a crane's hoist, scaled to lift tens of tonnes per cycle."),
            ("torque", "AC drive motors on the hoist, crowd, and swing systems all need to deliver sustained high torque against constantly changing digging resistance."),
            ("planetary-gears", "The swing and hoist drives use planetary reduction gearing to handle the shovel's enormous torque within a compact drivetrain housing."),
        ],
        "performance": [("Dipper capacity", "58.3 – 67.6 m³"), ("Nominal payload", "108.9 t"), ("Typical truck match", "218 – 363 t haul trucks"), ("Drive type", "AC electric")],
        "examples": [("Capstone Mantoverde, Chile", "4100XPC shovels have been deployed specifically to reduce truck queueing times at this copper operation."), ("In-pit crusher-conveyor operations", "The 4100XPC's payload is also sized to feed high-capacity in-pit crushing systems directly, bypassing trucks altogether on some sites.")],
        "facts": [
            "Its dipper alone can hold more material by volume than a small city bus.",
            "Rope shovels like this one are, mechanically, closer to a crane than to a hydraulic excavator — everything happens through wire rope tension, not hydraulic cylinders.",
            "It's engineered to load specific haul truck size classes in a target of three to four passes — fewer passes means less time each truck spends stationary being loaded.",
        ],
    },
    {
        "slug": "bertha-tbm", "title": "Bertha (Hitachi Zosen TBM)", "category": "underground-equipment",
        "summary": "At 17.5 metres in diameter, the largest earth-pressure-balance tunnel boring machine ever built, bored beneath downtown Seattle to replace the Alaskan Way Viaduct.",
        "purpose": "Purpose-built for a single bore beneath downtown Seattle — replacing an earthquake-damaged viaduct without digging up the street above it.",
        "scale": (17.5, "cutterhead diameter"),
        "stats": [("Diameter", "17.5 m"), ("Length", "99 m"), ("Weight", "~6,700 t"), ("Cutting disks", "600")],
        "history": "Hitachi Zosen built Bertha in Osaka for the Washington State Department of Transportation's Alaskan Way Viaduct replacement project, assembling it in Seattle in mid-2013 for a single, purpose-specific bore. It began tunnelling in July 2013, suffered a major mechanical failure after roughly 1,000 feet that halted work for about two years while it was partially disassembled and repaired in place, and finally completed its bore in 2017.",
        "components": [
            ("Cutterhead", "A rotating steel face fitted with 600 cutting disks that grind directly into the soil and rock ahead of the machine."),
            ("Earth-pressure-balance chamber", "A sealed chamber behind the cutterhead that holds excavated material under controlled pressure, balancing the ground's own pressure to prevent surface collapse above the tunnel."),
            ("Screw conveyor", "Removes spoil from the pressurised chamber at a controlled rate without releasing that pressure suddenly."),
            ("Thrust rams", "Hydraulic rams that push the entire machine forward against the finished tunnel lining behind it, segment by segment."),
        ],
        "how_it_works": "The cutterhead rotates continuously, its 600 disks fracturing soil and soft rock as thrust rams push the whole machine forward. Excavated spoil passes into the earth-pressure-balance chamber immediately behind the cutterhead, where it's deliberately kept under pressure matching the surrounding ground — too little pressure and the tunnel face can collapse; too much and it can heave the street above. A screw conveyor bleeds spoil out of that chamber at a metered rate for removal, while precast concrete segments are erected behind the machine to line the tunnel as it advances, one ring at a time.",
        "principles": [
            ("torque", "The cutterhead needed roughly 147,000 kN·m of torque to turn 600 grinding disks against a full-face resistance of soil and rock — among the highest torque figures of any machine on this site."),
            ("bearings", "The main cutterhead bearing carries the entire rotating cutting load while sealing out extreme ground pressure and groundwater, one of the most demanding bearing applications in any machine."),
            ("planetary-gears", "The cutterhead's drive train uses staged planetary reduction gearing to turn high-speed electric or hydraulic motor output into the cutterhead's slow, immense-torque rotation."),
        ],
        "performance": [("Diameter", "17.5 m (57.5 ft)"), ("Length", "99 m"), ("Weight", "~6,100 t"), ("Installed power", "22,000 kW"), ("Max thrust", "392,000 kN"), ("Max cutterhead torque", "147,000 kN·m")],
        "examples": [("SR 99 tunnel, Seattle", "Bertha's sole project: a roughly 2.9 km tunnel beneath downtown Seattle, replacing the earthquake-damaged Alaskan Way Viaduct.")],
        "facts": [
            "Bertha's mid-project breakdown, caused by a steel pipe casing that overheated its main bearing seals, halted the project for about two years while repair crews dug an access shaft down to the machine to fix it in place.",
            "At $80 million, Bertha was purpose-built for a single tunnel and was disassembled after completing it — TBMs of this size are rarely reused elsewhere.",
            "Its 600 cutting disks needed periodic replacement even mid-bore, accessed by workers entering the pressurised cutterhead chamber directly.",
        ],
    },
    {
        "slug": "sarens-sgc-250", "title": "Sarens SGC-250 “Big Carl”", "category": "industrial-material-handling",
        "summary": "A purpose-built ring crane with a 5,000-tonne maximum lifting capacity, currently the largest land-based crane in the world.",
        "purpose": "Exists for the single mega-lift that would otherwise take weeks of piecemeal crane work — built specifically for projects like Hinkley Point C's prefabricated reactor modules.",
        "scale": (250, "max height with jib extended (a working reach, not a parked height)"),
        "stats": [("Max capacity", "5,000 t"), ("Max boom length", "160 m"), ("Max height", "250 m"), ("Ground pressure system", "Ring-supported, not standard crawlers")],
        "history": "Sarens developed the SGC-250 (Sarens Giant Crane, 250,000 tonne-metre capacity) specifically for a handful of megaprojects too large for any existing mobile or crawler crane, most prominently the Hinkley Point C nuclear power station in the UK, where it lifts entire prefabricated reactor-building modules in single picks that would otherwise require weeks of piecemeal assembly.",
        "components": [
            ("Ring beam", "A large-diameter ring the crane's upper structure rotates on and derives its stability from, rather than a conventional crawler undercarriage."),
            ("Main boom", "A lattice boom up to 160 metres long, supplemented by an additional 100-metre heavy-duty jib for extreme-reach lifts."),
            ("Counterweight system", "Enormous, precisely positioned counterweight blocks that balance the load moment at the boom's far end."),
            ("Modular transport sections", "Every major component ships and assembles in sections, because the assembled crane itself is far too large to move as one unit."),
        ],
        "how_it_works": "Rather than resting the whole crane on crawler tracks the way conventional crawler cranes do, the SGC-250's upper structure rotates on a large ground-level ring, spreading the enormous combined weight of crane and load across a wider footprint than crawlers alone could manage. Hoist winches raise the load via wire rope run through the boom's rigging exactly as on any crane, just at a scale where a single lift can be an entire preassembled building module rather than a beam or a machine part.",
        "principles": [
            ("mechanical-advantage", "Its hoist system is wire-rope mechanical advantage taken to an extreme, multiple rope falls sharing a 5,000-tonne load across the rigging."),
            ("torque", "Slewing an assembly this size — crane and load together — demands sustained, carefully controlled torque to start and stop rotation without inducing dangerous load swing."),
            ("hydraulic-cylinders", "Boom angle and jib adjustments are made through large hydraulic cylinders, even though the primary hoisting force comes from wire rope rather than hydraulics."),
        ],
        "performance": [("Max lifting capacity", "5,000 t (at 40 m radius)"), ("Load moment", "250,000 t·m"), ("Capacity at 100 m radius", "2,000 t"), ("Max boom length", "160 m"), ("Max height", "250 m")],
        "examples": [("Hinkley Point C, United Kingdom", "Big Carl lifts entire prefabricated nuclear reactor building modules, some individually weighing over 700 tonnes, directly into position.")],
        "facts": [
            "It's nicknamed \"Big Carl\" after a Sarens project manager, not for any technical reason.",
            "At full height with its jib extended, it can lift loads roughly 250 metres in the air — taller than most skyscrapers.",
            "Because its footprint is so large, the crane effectively becomes part of a project's civil-engineering plan: the ground beneath its ring often has to be specially prepared to bear the load.",
        ],
    },
    {
        "slug": "kalmar-dcg330", "title": "Kalmar DCG330", "category": "industrial-material-handling",
        "summary": "A heavy industrial forklift built for handling loaded shipping containers and other massive loads at ports and intermodal yards, at nearly ten times the capacity of a typical warehouse forklift.",
        "purpose": "Built to lift what a standard warehouse forklift never could — a fully loaded shipping container — without needing a dedicated overhead crane at every terminal.",
        "scale": (4.5, "overall height, mast lowered (sources range 3.4 – 7.0 m by mast option)"),
        "stats": [("Lift capacity", "up to 33 t"), ("Typical load", "Loaded shipping containers"), ("Drive modes", "Multiple, operator-selectable"), ("Environment", "Ports, heavy industrial yards")],
        "history": "Kalmar's heavy forklift range grew directly out of the container-shipping boom of the late 20th century: standard forklifts topped out at a few tonnes, nowhere near enough to lift a fully loaded ISO shipping container, so an entirely separate class of purpose-built heavy forklift emerged around ports and rail yards. The DCG180–330 series sits at the top of that range, covering the heaviest loads a mast-type forklift, rather than a dedicated container handler, is asked to lift.",
        "components": [
            ("Reinforced mast", "A heavy-duty lifting mast engineered for loads many times a standard forklift's rating, without the excessive flex that would make precise container placement impossible."),
            ("Counterweight", "A substantial rear counterweight balancing the load moment of a multi-tonne container carried well forward of the front axle."),
            ("Variable hydraulic lift system", "Adjusts lift speed and force through the stroke, rather than applying constant hydraulic flow regardless of load."),
            ("Selectable drive modes", "Operator-selectable modes tuned for precision spotting versus faster yard travel between stacks."),
        ],
        "how_it_works": "A hydraulic lift cylinder raises the mast's carriage and forks, with lift speed and hydraulic pressure managed by a variable system that trades speed for smoother, more controlled placement as a load nears its final position. The rear counterweight, positioned well behind the drive axle, keeps the whole machine stable even with tonnes of container cantilevered out in front, exactly the same lever-balance principle behind every forklift regardless of size, just scaled to loads no ordinary warehouse machine could approach.",
        "principles": [
            ("hydraulic-cylinders", "The mast's lift cylinder is a direct, large-scale application of hydraulic linear force, sized for loads many times a standard forklift's."),
            ("pascals-law", "The same pressurised-fluid principle behind a small warehouse forklift scales up here simply by increasing cylinder bore, following Pascal's Law directly."),
            ("mechanical-advantage", "The rear counterweight and mast geometry together form a lever system balancing a forward, off-centre load against the machine's own weight."),
        ],
        "performance": [("Lift capacity", "18 – 33 t (model-dependent)"), ("Typical duty", "Loaded ISO shipping containers"), ("Primary environment", "Port terminals, heavy industrial yards")],
        "examples": [("Container terminals worldwide", "Heavy forklifts in this class handle loaded containers wherever a dedicated reach stacker or crane isn't already positioned for the job.")],
        "facts": [
            "A single loaded 40-foot shipping container can weigh over 30 tonnes — well beyond what any warehouse forklift could safely approach.",
            "Heavy forklifts like this trade the reach and stacking height of a dedicated container handler for tighter manoeuvring in congested yards.",
            "Multiple drive-mode settings let the same machine prioritise fuel efficiency on long yard runs or maximum control during a delicate stacking placement.",
        ],
    },
    {
        "slug": "jcb-541-70", "title": "JCB 541-70", "category": "construction-equipment",
        "summary": "A telescopic handler that combines a forklift's carrying capacity with a crane-like telescoping boom, reaching well beyond what any fixed-mast forklift could manage.",
        "purpose": "Exists to reach both up and out from one machine, covering jobs that would otherwise need a forklift for height and a separate crane for reach.",
        "scale": (7, "max lift height (boom raised; stowed transport height is ~2.5 m)"),
        "stats": [("Lift capacity", "4.1 t"), ("Max lift height", "7 m"), ("Boom type", "Single telescoping section"), ("Typical use", "Construction, agriculture")],
        "history": "Telehandlers emerged from the recognition that construction and farm sites often need to lift a load both up and out — over a wall, into an upper floor, or across a trench — something neither a forklift's vertical mast nor a crane's slower rigging handles well on its own. JCB, one of the type's pioneering manufacturers since the 1970s, has kept refining the format ever since; the 541-70 represents the mid-size class most common on general construction sites.",
        "components": [
            ("Telescoping boom", "A single hydraulically extending boom section that reaches both up and forward, rather than lifting straight up on a fixed mast."),
            ("Carriage & forks (or attachment)", "A quick-attach carriage that swaps between forks, a bucket, a man-basket, or other attachments for different tasks."),
            ("Stabiliser legs (on some models)", "Extend outward before a lift to widen the machine's effective base and prevent tipping at full reach."),
            ("All-wheel steering chassis", "Selectable two-wheel, four-wheel, and crab-steer modes for manoeuvring in tight yards or driving directly sideways."),
        ],
        "how_it_works": "A hydraulic cylinder inside the boom extends its telescoping section outward while separate lift cylinders raise the whole boom assembly, letting the load move through a combined up-and-out arc a fixed mast can't reach. Because reach and load both move the effective lever arm forward, load charts strictly limit how much weight can be carried at a given extension and height — the same machine that lifts 4.1 tonnes close to the chassis may be rated for a fraction of that at full boom extension.",
        "principles": [
            ("hydraulic-cylinders", "Boom extension, lift, and tilt are each driven by dedicated hydraulic cylinders working together through the telescoping structure."),
            ("mechanical-advantage", "Load capacity falls sharply as reach increases, precisely because extending the boom lengthens the lever arm the machine's own weight has to counterbalance."),
            ("gear-ratios", "The transmission's gear steps are tuned for low-speed, high-torque manoeuvring around a job site rather than road speed."),
        ],
        "performance": [("Max lift capacity", "4.1 t (at centre of gravity)"), ("Max lift height", "7 m"), ("Capacity at full height", "2.25 t"), ("Capacity at full forward reach", "1.5 t")],
        "examples": [("General construction sites worldwide", "Telehandlers in this class are among the most common single machines on a mid-size construction site, handling material lifts a forklift or crane individually couldn't cover as efficiently.")],
        "facts": [
            "A telehandler's rated capacity is never a single number — it changes continuously with boom angle and extension, published as a full load chart the operator must read before every lift.",
            "Because the boom reaches forward as well as up, a telehandler can place a load over an obstacle a straight-mast forklift would have to drive around.",
            "Crab steering, standard on many telehandlers, lets all wheels turn the same direction so the machine can move diagonally without changing its facing angle — useful in narrow site aisles.",
        ],
    },
    {
        "slug": "john-deere-x9-1100", "title": "John Deere X9 1100", "category": "agricultural-machinery",
        "summary": "John Deere's flagship combine harvester, built around a twin-rotor threshing system specifically to keep pace with the widest headers and highest field speeds in modern grain harvesting.",
        "purpose": "Built to remove the threshing bottleneck that limited how wide a header a combine could actually keep fed, so operators can harvest more acres inside a short weather window.",
        "scale": (3.5, "transport height (figure for the closely related X9 1000; the 1100 is likely very similar)"),
        "stats": [("Engine power", "690 hp"), ("Grain tank capacity", "16,210 L"), ("Rotors", "Twin 24-inch"), ("Peak unload rate", "5.3 bu/s")],
        "history": "Combine harvesters have grown steadily larger for the same reason every machine on this page has: a wider, faster machine covers more acres per labour-hour, which matters enormously during a harvest window that can close in days if weather turns. John Deere's X9 series, introduced in the early 2020s, was purpose-built around a completely new twin-rotor separation system specifically to remove the throughput bottleneck that limited how wide a header the company's previous single-rotor combines could actually keep fed.",
        "components": [
            ("Header", "The cutting and gathering front end, often 40 feet or wider, that severs and feeds crop into the machine."),
            ("Twin rotor threshing & separating system", "Two 24-inch rotors that thresh grain from the stalk and separate it from straw and chaff, in parallel rather than in series."),
            ("Cleaning shoe", "A shaking, air-blown sieve system that finishes separating clean grain from any remaining light material before it reaches the tank."),
            ("Grain tank & unloading auger", "A 16,210-litre tank and a high-rate auger that can unload into a grain cart without stopping the harvester."),
        ],
        "how_it_works": "The header cuts and feeds standing crop into the machine's throat, where it's carried up to the twin rotors. Each rotor threshes grain loose from the stalk through a combined rubbing-and-impact action, then flings the remaining material rearward across a separating grate that lets loose grain fall through while straw continues out the back. A cleaning shoe beneath then uses a shaking sieve and a controlled air blast to finish separating grain from chaff, and clean grain augers up into the tank, ready to be unloaded on the move via a high-capacity auger into a following grain cart.",
        "principles": [
            ("torque", "The 690 hp engine must deliver sustained torque to two large rotors and a wide header simultaneously, all while the machine drives forward through standing crop."),
            ("gear-ratios", "The hydrostatic transmission continuously varies its effective ratio to match ground speed to available engine power as crop density changes across a field."),
            ("bearings", "The twin rotors spin continuously at high speed for entire harvest days, making their bearings one of the machine's most heavily worked components."),
        ],
        "performance": [("Engine power", "690 hp (515 kW)"), ("Grain tank capacity", "16,210 L (460 bu)"), ("Peak unload rate", "5.3 bu/s (186.7 L/s)"), ("Rotor count/size", "2 × 24 in")],
        "examples": [("Large-scale grain operations, North America", "X9-class combines are aimed specifically at operations harvesting thousands of acres within a narrow weather window.")],
        "facts": [
            "Its twin-rotor system was John Deere's first major departure from single-rotor threshing, built specifically to unlock wider headers without the machine choking on its own crop flow.",
            "The grain tank alone can hold over 16,000 litres — roughly the volume of a small backyard swimming pool.",
            "A modern flagship combine like this one can harvest in a single day what would have taken a horse-drawn binder crew the better part of a season a century ago.",
        ],
    },
    {
        "slug": "john-deere-9rx", "title": "John Deere 9RX", "category": "agricultural-machinery",
        "summary": "John Deere's largest row-crop tractor, running on four independent tracks instead of wheels to put record horsepower onto soft ground without compacting it.",
        "purpose": "Exists to put record horsepower on the ground without compacting the soil underneath it — the one trade-off a wheeled tractor at this power level can't avoid.",
        "scale": (3.9, "transport height (varies slightly by 9RX model variant)"),
        "stats": [("Max horsepower", "830 hp"), ("Track configuration", "4-track articulated"), ("Hydraulic flow", "168 gal/min"), ("Max ballast", "up to 84,000 lb")],
        "history": "John Deere's 9RX line pushed row-crop tractor horsepower to new highs through the 2010s and 2020s specifically by pairing ever-larger engines with four-track undercarriages instead of the twin-track or wheeled designs common at lower power levels — more contact area spreads the same weight over more soil, reducing the compaction that otherwise undoes much of the benefit of a bigger tractor. The current top model, the 9RX 830, tops the lineup at 830 horsepower.",
        "components": [
            ("Four independent tracks", "Rather than two wide tracks or four wheels, four separate track units at each corner spread ground pressure further and improve flotation on soft or wet fields."),
            ("JD18 engine", "An 18-litre diesel meeting Final Tier 4/Stage V emissions standards without needing diesel exhaust fluid, using exhaust-gas recirculation instead."),
            ("CVT or powershift transmission", "Delivers continuously or near-continuously variable ground speed to match engine power to whatever implement is attached."),
            ("Hydraulic remotes", "Up to 168 gallons per minute of hydraulic flow available to power large towed implements like air seeders or wide sprayers."),
        ],
        "how_it_works": "The JD18 diesel's torque and power route through the transmission to all four track units, each driven independently enough to handle articulated steering without a conventional differential's compromises. Because the tractor's full weight — plus up to 84,000 lb of add-on ballast for maximum drawbar pull — is spread across four tracks rather than concentrated under four tyres, ground pressure per square inch stays low enough to pull heavy, wide implements through a field without the tracks themselves compacting the soil the crop depends on.",
        "principles": [
            ("torque-converters", "Depending on transmission configuration, torque-converter or CVT drive smooths power delivery as pulling load varies across a field."),
            ("final-drives-differentials", "Each track unit has its own final drive delivering the tractor's very high torque down to track speed, without a conventional differential between left and right sides."),
            ("four-stroke-diesel-cycle", "The JD18's 830 horsepower comes from the same four-stroke diesel cycle as any smaller farm engine, scaled up and heavily turbocharged."),
        ],
        "performance": [("Max engine power", "830 hp"), ("Engine displacement", "18 L (JD18)"), ("Hydraulic flow", "168 gal/min"), ("Max ballast", "84,000 lb")],
        "examples": [("Large-scale row-crop operations, North American plains", "9RX-class tractors are built specifically for operations pulling the widest tillage, seeding, and application implements across thousands of acres.")],
        "facts": [
            "Four independent tracks let the 9RX articulate for tight headland turns the way a wheeled articulated tractor does, without losing the flotation advantage tracks provide.",
            "At 830 hp, the top 9RX model rivals the output of a small fleet of ordinary farm tractors combined, delivered from a single engine.",
            "Reducing soil compaction isn't a comfort feature — compacted soil restricts root growth and drainage for years, so flotation directly protects future yields, not just the current pass.",
        ],
    },
    {
        "slug": "john-deere-r4045", "title": "John Deere R4045", "category": "agricultural-machinery",
        "summary": "A self-propelled sprayer built to cover wide swaths of cropland quickly and precisely, applying crop protection products through booms that can stretch well beyond a football field's width.",
        "purpose": "Built to apply crop protection across an entire field width in a fraction of the passes a smaller sprayer would need, when a treatment window can close in days.",
        "scale": (4.0, "estimated overall height — manufacturer spec not found (only ground clearance, 1.47 m, is documented)"),
        "stats": [("Engine power", "346 hp"), ("Tank capacity", "1,200 gal"), ("Boom width", "90 – 120 ft"), ("Max application rate", "230 gal/min")],
        "history": "Self-propelled sprayers replaced towed, tractor-pulled sprayers for large operations because a dedicated chassis can be built taller (clearing standing crop without damaging it), lighter per unit of ground pressure, and faster across the field between fills. John Deere introduced the R4045 as, at the time, the largest sprayer in its Class 4 lineup, built specifically around wider booms and a bigger tank than the machines it replaced.",
        "components": [
            ("Boom", "A dual swing-link suspended boom, available up to 120 feet wide, engineered to flex with field terrain without the tips gouging the ground."),
            ("Solution tank", "A 1,200-gallon tank carrying the diluted crop-protection product being applied."),
            ("High-flow spray pump", "Delivers up to 230 gallons per minute across the full boom width at the sprayer's working speed."),
            ("Four-wheel hydrostatic drive", "Independent hydraulic drive to each wheel, giving the tall, narrow-footprint sprayer stable traction and tight turning despite its height."),
        ],
        "how_it_works": "A hydraulic pump draws diluted product from the tank and delivers it under pressure to nozzles spaced along the full boom width, metered against the sprayer's ground speed so each section of field receives a consistent application rate regardless of whether the machine speeds up or slows down. The boom itself floats on a suspended linkage that lets it flex over uneven ground while keeping nozzle height — and therefore spray pattern — consistent, while four-wheel hydrostatic drive lets the tall machine straddle standing row crops without a single mechanical driveshaft running the width of the chassis.",
        "principles": [
            ("hydraulic-cylinders", "Boom fold, unfold, and height adjustment are all driven by hydraulic cylinders, letting a 120-foot boom collapse to a legal road width in minutes."),
            ("pascals-law", "The spray pump's pressure delivery follows the same fluid-pressure principles as any hydraulic system, just moving crop-protection solution instead of oil."),
            ("bearings", "The boom's suspension pivots and the drive system's wheel motors both depend on bearings surviving constant field vibration for an entire season."),
        ],
        "performance": [("Engine power", "346 hp"), ("Tank capacity", "1,200 gal"), ("Boom width options", "90, 100, or 120 ft"), ("Max application rate", "230 gal/min"), ("Transport speed", "35 mph")],
        "examples": [("Large-scale row-crop farms, North America", "R4045-class sprayers are built for operations that need to complete a full application pass across thousands of acres within a narrow weather and growth-stage window.")],
        "facts": [
            "A fully unfolded 120-foot boom is wider than most residential city blocks are deep.",
            "Sprayers like this are built tall and narrow specifically to straddle rows of standing crop without crushing it, unlike almost every other machine on this site, which is built low and wide for stability.",
            "Application timing is often more urgent than harvest timing — a pest or disease window can close in days, which is exactly why sprayer road-transport speed and boom-fold time both matter as much as tank size.",
        ],
    },
    {
        "slug": "epiroc-pv351", "title": "Epiroc Pit Viper 351", "category": "mining-equipment",
        "summary": "A rotary blasthole drill rig built to bore the deep, wide holes mines fill with explosives to fracture rock ahead of loading — one of the largest rotary drills in regular production.",
        "purpose": "Exists purely to prepare rock for blasting — drilling the holes a mine later fills with explosives, a job that has to finish before any of the site's excavators can start.",
        "scale": (19.8, "mast height, approximated from single-pass drill depth"),
        "stats": [("Hole diameter", "270 – 406 mm"), ("Single-pass depth", "19.8 m"), ("Bit load capacity", "56.7 t"), ("Drilling method", "Rotary tricone")],
        "history": "Rotary blasthole drilling replaced older percussion drilling methods at large open-pit mines because rotary bits, under enough downward force, cut faster and more consistently through hard rock at the diameters mine blasting patterns actually need. Atlas Copco (now Epiroc, after the 2018 split) developed the Pit Viper line specifically for this large-diameter, high-productivity segment, with the 351 sitting near the top of the range.",
        "components": [
            ("Rotary head", "Applies both downward force (bit load) and rotation to the drill string simultaneously, the two things a tricone bit needs to cut rock efficiently."),
            ("Tricone drill bit", "Three cone-shaped cutting elements that roll and crush rock as the string rotates, standard for large-diameter blasthole drilling."),
            ("Mast", "A tall vertical structure holding the drill string, tall enough to handle a full single-pass depth of nearly 20 metres without adding sections."),
            ("Air compressor system", "Delivers high-volume compressed air down the drill string to clear cuttings from the hole and cool the bit."),
        ],
        "how_it_works": "The rotary head clamps onto the drill string and applies both rotation and substantial downward force — up to 56.7 tonnes of bit load — driving the tricone bit's three rolling cutters into the rock face. Compressed air, pumped down through the hollow drill string at up to 3,800 cubic feet per minute, escapes through the bit and carries rock cuttings back up the annulus around the drill string and out of the hole, keeping the bit clear and cool as it advances. Once a hole reaches its target depth, it's charged with explosives as part of a wider blast pattern designed to fracture rock for loading by shovels or excavators.",
        "principles": [
            ("torque", "The rotary head must deliver sustained torque to keep three rolling cutters biting into hard rock without stalling, all while also pressing down with tens of tonnes of bit load."),
            ("hydraulic-cylinders", "Mast raising, drill-string clamping, and rod-handling functions are all hydraulically actuated."),
            ("bearings", "The tricone bit's own rolling cutters ride on sealed bearings that must survive continuous rock-crushing loads at the very tip of the drill string, in the harshest environment on the whole machine."),
        ],
        "performance": [("Hole diameter range", "270 – 406 mm"), ("Single-pass depth", "19.8 m"), ("Multi-pass depth", "up to 41.1 m"), ("Bit load capacity", "56.7 t"), ("Air capacity", "3,800 cfm at 110 psi")],
        "examples": [("Large open-pit metal and coal mines worldwide", "Pit Viper-class rigs drill blast patterns across benches ahead of shovel-and-truck loading fleets.")],
        "facts": [
            "The pattern and depth of every hole a rig like this drills is planned in advance as part of a full blast design — drilling isn't improvised, it follows an engineered grid.",
            "Bit load, not rotation speed, is usually the limiting factor in tricone drilling productivity: more downward force generally cuts rock faster than spinning the bit harder.",
            "A single rig can drill dozens of holes in a shift, each one eventually packed with explosive and tied into a single, precisely timed blast.",
        ],
    },
    {
        "slug": "ponsse-bear", "title": "Ponsse Bear", "category": "forestry-machinery",
        "summary": "An eight-wheeled forest harvester built to fell, delimb, and cut trees to length in a single continuous operation, sized for the largest timber a wheeled harvester is asked to handle.",
        "purpose": "Built for timber too large for Ponsse's mid-size harvesters, doing the felling, delimbing, and cutting-to-length in one pass instead of three separate machine trips.",
        "scale": (3.86, "overall height, top of cab"),
        "stats": [("Engine power", "354 hp"), ("Wheel configuration", "8-wheel"), ("Harvester head", "Felling, delimbing, bucking"), ("Engine torque", "1,450 N·m")],
        "history": "Mechanised harvesting replaced chainsaw felling crews across much of the industrialised forestry world from the late 20th century onward, driven by the same labour-productivity and safety logic behind every large machine on this site. Ponsse, a Finnish forestry-equipment specialist, introduced the Bear as its largest harvester specifically to handle bigger timber than its mid-size models, using an eight-wheel chassis for the flotation and stability that size of tree demands.",
        "components": [
            ("Harvester head", "A hydraulically actuated head mounted on the crane that grips, fells, delimbs, and cuts a tree to length, all without the operator leaving the cab."),
            ("Crane", "Positions the harvester head at the tree and moves it through the felling and processing sequence."),
            ("Eight-wheel chassis", "Larger footprint than a six-wheel harvester, spreading weight further across forest floor that can be soft, uneven, or environmentally sensitive."),
            ("Mercedes-Benz/MTU engine", "A 7.7-litre diesel delivering up to 354 hp and 1,450 N·m of torque to both propulsion and the crane's hydraulic system."),
        ],
        "how_it_works": "The crane swings the harvester head to a standing tree, where powered rollers and a felling chain or bar grip and fell it in one motion. As the tree is drawn through the head, delimbing knives strip branches from the trunk in a continuous pass, and an onboard measuring system tracks length so the head's saw can cut the trunk into pre-programmed log lengths automatically, optimising each tree's value before it's ever set down. The whole sequence — fell, delimb, buck — happens in the time it takes the crane to reach the next tree.",
        "principles": [
            ("hydraulic-cylinders", "Every function of the harvester head — gripping, felling, delimbing pressure, and the crane's own movement — is hydraulically driven."),
            ("pascals-law", "The harvester head's grip and delimb-knife pressure both rely on the same fluid-pressure principle that scales force through a hydraulic circuit."),
            ("torque", "The engine's 1,450 N·m of torque has to serve both propulsion over rough forest terrain and the crane's hydraulic pumps simultaneously."),
        ],
        "performance": [("Engine power", "354 hp (260 kW)"), ("Engine torque", "1,450 N·m"), ("Wheel configuration", "8×8"), ("Fuel tank", "400 L")],
        "examples": [("Nordic and North American commercial forestry operations", "Bear-class harvesters are deployed on sites with larger average tree size, where a mid-size harvester's head and chassis would be undersized for the timber.")],
        "facts": [
            "A single harvester head can process a tree from standing timber to cut-to-length logs in well under a minute for typical stems.",
            "The onboard measuring system can optimise cutting lengths in real time to maximise the value of each log, based on current timber prices and mill specifications loaded into the machine.",
            "Eight-wheel forestry machines like the Bear are specifically chosen over six-wheel models on sites with soft or environmentally sensitive ground, where the extra wheels reduce rutting.",
        ],
    },
    {
        "slug": "konecranes-rtg", "title": "Konecranes RTG", "category": "industrial-material-handling",
        "summary": "A rubber-tyred gantry crane that straddles multiple lanes of stacked shipping containers, moving on its own tyres between container blocks rather than running on fixed rails.",
        "purpose": "Exists to keep a container yard's stacks organised and moving without needing fixed rail infrastructure, repositioning between blocks under its own power as vessel schedules shift.",
        "scale": (25, "estimated structure height — no manufacturer spec found; derived from clearing six stacked containers plus the beam and hoist"),
        "stats": [("Lifting capacity", "up to 65 t under spreader"), ("Span", "up to 8 container rows + truck lane"), ("Stack height", "up to 1-over-6"), ("Power options", "Diesel, hybrid, electric, battery")],
        "history": "Container terminals adopted gantry cranes broadly as container shipping scaled through the late 20th century, needing something faster and more space-efficient than mobile cranes or forklifts stacking boxes several high. Rubber-tyred gantries in particular offered an advantage rail-mounted gantries couldn't: the ability to reposition between different container blocks without fixed rail infrastructure, at some cost in precision and speed compared to a railed system.",
        "components": [
            ("Gantry legs & rubber-tyred bogies", "Four (or more) corner legs on independently steerable rubber-tyred wheel sets, letting the whole crane reposition between container rows under its own power."),
            ("Spreader", "A hydraulically actuated frame that locks onto a shipping container's four corner castings for lifting."),
            ("Hoist trolley", "Travels along the gantry's overhead beam, positioning the spreader across the crane's full span."),
            ("Active load control system", "Software-controlled damping that counteracts container sway during hoisting and trolley travel."),
        ],
        "how_it_works": "The crane straddles a block of stacked containers on its rubber-tyred legs, wide enough to span up to eight container rows plus an additional truck lane. A hoist trolley runs along the overhead beam to position the spreader directly above the target container, lowers and locks onto its corner castings, then lifts and traverses the load to its new position — either stacking it within the block or setting it onto a waiting truck chassis in the lane below. Active load control uses the trolley and hoist drives themselves to damp out the pendulum swing a suspended container would otherwise develop, letting operators place loads precisely without waiting for the sway to settle naturally.",
        "principles": [
            ("gear-ratios", "The hoist and trolley drives use geared reduction to turn electric motor speed into the controlled lifting and travel speeds container handling requires."),
            ("mechanical-advantage", "The hoist wire-rope reeving multiplies motor force exactly as any crane's rigging does, scaled to a rated capacity of up to 65 tonnes under the spreader."),
            ("torque", "Each independently steerable wheel bogie needs its own drive torque to manoeuvre the whole gantry structure squarely between container rows."),
        ],
        "performance": [("Lifting capacity under spreader", "up to 65 t"), ("Span", "up to 8 rows + truck lane"), ("Stacking height", "1-over-6"), ("Power options", "Diesel, hybrid, electric, battery")],
        "examples": [("Container terminals worldwide", "RTGs are the dominant container-stacking crane type at ports where fixed rail infrastructure for rail-mounted gantries isn't justified by traffic volume.")],
        "facts": [
            "Because RTGs move on tyres rather than rails, an entire container yard's crane fleet can be reorganised between blocks as vessel schedules and volumes shift.",
            "Active load control systems can cut container-placement time meaningfully by eliminating the wait for natural pendulum sway to die down after each lift.",
            "RTGs increasingly run on electric or hybrid power specifically to cut the diesel exhaust and noise of running large engines continuously in a busy container yard.",
        ],
    },
    {
        "slug": "m1150-abv", "title": "M1150 Assault Breacher Vehicle", "category": "military-engineering-vehicles",
        "summary": "A U.S. military combat engineering vehicle built on the M1 Abrams tank chassis, purpose-designed to clear paths through minefields and obstacle belts ahead of advancing forces.",
        "purpose": "Built for exactly one mission: clearing a path through mines and obstacle belts before anyone else in the formation has to cross them.",
        "scale": (3.0, "estimated overall height — reliable spec not found for the Abrams hull plus stowed mine-clearing gear"),
        "stats": [("Base chassis", "M1A1 Abrams"), ("Weight", "~72 t"), ("Engine", "Honeywell AGT1500C, 1,500 hp"), ("Primary tools", "Mine plow, line charges")],
        "history": "Combat engineering vehicles built on main battle tank chassis date back decades, on the logic that a vehicle clearing a path under fire needs the same armour protection as the tanks following behind it. The M1150 ABV replaced earlier, less-protected mine-clearing vehicles by mounting breaching equipment directly onto a standard M1A1 Abrams hull, giving breaching crews the same survivability as the armoured units they support.",
        "components": [
            ("Full-width mine plow", "A hydraulically actuated plow blade that digs into the ground ahead of the vehicle, physically displacing buried mines out of the vehicle's path."),
            ("Mine-clearing line charge (MICLIC) launchers", "Rocket-propelled explosive line charges that detonate across a path ahead of the vehicle, clearing mines and obstacles over a distance no plow alone could cover as quickly."),
            ("AGT1500C gas turbine engine", "The same 1,500 hp multi-fuel turbine engine used in the M1 Abrams, retained here for shared logistics and parts commonality."),
            ("Modified hull (no main gun turret)", "The Abrams' turret and main gun are removed and replaced with the breaching equipment and a remote weapon station."),
        ],
        "how_it_works": "Approaching an obstacle belt, the ABV's crew can fire a rocket-propelled mine-clearing line charge ahead of the vehicle; the rocket drags a long explosive-filled hose across the ground, and detonating it clears a path by exploding or displacing buried mines across that whole length in a single event. For obstacles the line charge doesn't fully clear, or once a general lane is established, the vehicle's full-width mine plow drops and physically pushes any remaining buried mines or debris aside as the vehicle advances, both operations conducted from behind the same armour protection as the Abrams tanks it's built alongside.",
        "principles": [
            ("torque-converters", "The Abrams-derived transmission uses a torque converter to deliver smooth, stallable power to a 72-tonne vehicle across the same range of ground conditions the base tank handles."),
            ("final-drives-differentials", "Track final drives, shared with the base M1 Abrams platform, deliver the last torque multiplication to each track at this vehicle's very high combat weight."),
            ("hydraulic-cylinders", "The mine plow's raising, lowering, and depth control are all hydraulically actuated."),
        ],
        "performance": [("Weight", "~72 t"), ("Engine", "AGT1500C gas turbine, 1,500 hp"), ("Top speed", "42 mph (67 km/h)"), ("Crew", "2")],
        "examples": [("U.S. Army and Marine Corps combat engineer units", "The ABV equips dedicated breaching companies tasked with opening lanes through minefields and obstacles ahead of manoeuvre forces.")],
        "facts": [
            "Its gas turbine engine, shared with the M1 Abrams, can run on multiple fuel types — a deliberate logistics choice for a vehicle that has to keep running wherever the tanks it supports are refuelled.",
            "A single MICLIC rocket-and-line-charge system can clear a path roughly 100 metres long and 14 metres wide in one detonation.",
            "Removing the Abrams' turret and main gun to fit breaching equipment means the ABV relies on the armoured units around it for direct firepower, carrying only a remote-operated machine gun for self-defence.",
        ],
    },
    {
        "slug": "spartacus-dredger", "title": "Spartacus (Cutter Suction Dredger)", "category": "special-purpose-machines",
        "summary": "The most powerful cutter suction dredger ever built, and the first in the world powered by LNG, engineered to cut through harder seabed material at greater depth than any dredger before it.",
        "purpose": "Exists to cut through harder seabed material at greater depth than any dredger before it, while running on a fuel — LNG — nothing else in its class used yet.",
        "scale": (10, "moulded depth, hull only (keel to main deck; masts and gantry above deck add more but aren't documented)"),
        "stats": [("Installed power", "44,180 kW"), ("Length", "164 m"), ("Max dredging depth", "45 m"), ("Fuel", "LNG (first of its kind)")],
        "history": "Belgian dredging contractor DEME commissioned Spartacus from Dutch shipbuilder Royal IHC specifically to reach seabed material at depths and hardness beyond what the existing dredging fleet could economically handle, delivered in 2019 as, at the time, the most powerful cutter suction dredger in the world. Its LNG propulsion was a deliberate first for the class, aimed at cutting emissions from a vessel that otherwise burns enormous amounts of fuel continuously during operation.",
        "components": [
            ("Cutterhead", "A rotating, toothed cutting wheel at the end of a ladder that breaks up seabed material, from soft silt to hard rock, ahead of suction."),
            ("Suction and discharge pumps", "High-capacity pumps that draw the cut material, mixed with water, up through the suction pipe and discharge it via pipeline to its placement site."),
            ("Ladder", "The structure lowering the cutterhead to the working depth, engineered here to reach 45 metres — significantly deeper than most cutter suction dredgers."),
            ("Onboard maintenance workshop", "A vibration-insulated workshop that lets crews service and repair cutterheads during operations, without returning to port."),
        ],
        "how_it_works": "The cutterhead, lowered on its ladder to the seabed, rotates and swings side to side across the working face, its teeth breaking up material from soft sediment up to hard rock. Powerful suction pumps immediately draw the loosened material, mixed with water into a slurry, up through the suction pipe, and discharge pumps push that slurry through a pipeline — sometimes kilometres long — to wherever it's being placed, whether that's a land reclamation site or a disposal ground. Spartacus's exceptional installed power lets it maintain cutting speed through harder material and at greater depth than dredgers with less power available at the cutterhead.",
        "principles": [
            ("torque", "The cutterhead drive must sustain very high torque cutting into hard seabed rock, the underwater equivalent of a tunnel boring machine's cutterhead demands."),
            ("bearings", "The cutterhead's drive shaft and the ladder's pivot both rely on bearings sealed against constant seawater immersion, one of the harshest bearing environments of any machine on this site."),
            ("hydraulic-cylinders", "Ladder raising and lowering, along with several onboard handling systems, are hydraulically actuated."),
        ],
        "performance": [("Total installed power", "44,180 kW"), ("Length", "164 m"), ("Max dredging depth", "45 m"), ("Propulsion", "LNG-fuelled")],
        "examples": [("Land reclamation and deepening projects worldwide", "Spartacus is deployed on projects specifically requiring depth or seabed hardness beyond older dredgers' practical limits.")],
        "facts": [
            "Before Spartacus, the practical depth limit for most cutter suction dredgers was around 35 metres — Spartacus pushed that to 45.",
            "It was the world's first LNG-powered cutter suction dredger, a fuel choice aimed squarely at reducing the vessel's substantial continuous emissions.",
            "Its onboard workshop lets a damaged cutterhead be repaired at sea, avoiding the costly transit back to port that would otherwise idle a vessel this expensive.",
        ],
    },
]


def esc(s):
    return s


def stat_row(stats):
    cells = "".join(
        '<div class="stat"><span class="l">%s</span><span class="v">%s</span></div>' % (k, v)
        for k, v in stats
    )
    return '<div class="stat-row">%s</div>' % cells


# Illustrative human reference points used only for the hero "scale comparison" —
# an average adult's height/weight/hand-twist, not a spec of any machine.

# Simplified blueprint-style side-profile silhouettes, one per machine, hand-drawn from
# each machine's own real proportions (not traced from any photo). Each entry is
# (local_width, local_height, svg_fragment) in a top-left-origin coordinate system
# where y = local_height is the ground line the machine stands on.
INK, BLUE, BLUESOFT, MID = "#151a1f", "#2454c7", "#e8edfb", "#5b6672"
SILHOUETTES = {
    "liebherr-r9800": (200, 104, (
        '<rect x="10" y="92" width="160" height="12" fill="%s"/>'
        '<rect x="68" y="55" width="55" height="37" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="74" y="62" width="20" height="14" fill="%s"/>'
        '<polyline points="95,55 148,22 178,48" fill="none" stroke="%s" stroke-width="6" stroke-linecap="round"/>'
        '<polyline points="178,48 196,80" fill="none" stroke="%s" stroke-width="5" stroke-linecap="round"/>'
        '<polygon points="188,72 206,72 202,92 186,90" fill="%s"/>'
    ) % (INK, BLUESOFT, BLUE, MID, INK, INK, MID)),
    "caterpillar-d11": (190, 84, (
        '<rect x="5" y="72" width="150" height="12" fill="%s"/>'
        '<rect x="45" y="42" width="90" height="32" fill="%s" stroke="%s" stroke-width="2"/>'
        '<polygon points="5,50 28,40 33,74 10,74" fill="%s"/>'
        '<rect x="95" y="20" width="30" height="24" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="127" y="10" width="5" height="20" fill="%s"/>'
    ) % (INK, BLUESOFT, BLUE, MID, BLUESOFT, BLUE, INK)),
    "caterpillar-994k": (200, 98, (
        '<circle cx="150" cy="82" r="16" fill="%s"/>'
        '<circle cx="72" cy="82" r="16" fill="%s"/>'
        '<rect x="95" y="42" width="80" height="38" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="125" y="20" width="30" height="24" fill="%s" stroke="%s" stroke-width="2"/>'
        '<polyline points="98,52 45,32" fill="none" stroke="%s" stroke-width="6" stroke-linecap="round"/>'
        '<polygon points="14,20 48,20 42,50 10,46" fill="%s"/>'
    ) % (INK, INK, BLUESOFT, BLUE, BLUESOFT, BLUE, INK, MID)),
    "caterpillar-24m": (220, 89, (
        '<rect x="30" y="40" width="160" height="18" fill="%s" stroke="%s" stroke-width="2"/>'
        '<circle cx="48" cy="80" r="9" fill="%s"/>'
        '<circle cx="168" cy="80" r="9" fill="%s"/>'
        '<circle cx="190" cy="80" r="9" fill="%s"/>'
        '<rect x="68" y="18" width="28" height="24" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="172" y="28" width="32" height="14" fill="%s"/>'
        '<rect x="95" y="58" width="50" height="9" fill="%s"/>'
    ) % (BLUESOFT, BLUE, INK, INK, INK, BLUESOFT, BLUE, MID, MID)),
    "caterpillar-797f": (210, 108, (
        '<rect x="20" y="68" width="170" height="14" fill="%s"/>'
        '<circle cx="45" cy="90" r="14" fill="%s"/>'
        '<circle cx="150" cy="92" r="16" fill="%s"/>'
        '<circle cx="182" cy="92" r="16" fill="%s"/>'
        '<polygon points="50,68 62,24 190,15 190,68" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="20" y="45" width="26" height="24" fill="%s"/>'
    ) % (INK, INK, INK, INK, BLUESOFT, BLUE, MID)),
    "big-muskie-dragline": (230, 186, (
        '<rect x="30" y="150" width="140" height="28" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="35" y="176" width="20" height="10" fill="%s"/>'
        '<rect x="140" y="176" width="20" height="10" fill="%s"/>'
        '<line x1="60" y1="150" x2="210" y2="25" stroke="%s" stroke-width="6" stroke-linecap="round"/>'
        '<line x1="205" y1="35" x2="188" y2="125" stroke="%s" stroke-width="2"/>'
        '<polygon points="172,122 202,122 196,142 178,140" fill="%s"/>'
    ) % (BLUESOFT, BLUE, INK, INK, INK, MID, MID)),
    "bagger-293": (260, 132, (
        '<rect x="20" y="122" width="26" height="10" fill="%s"/>'
        '<rect x="52" y="122" width="26" height="10" fill="%s"/>'
        '<rect x="84" y="122" width="26" height="10" fill="%s"/>'
        '<rect x="116" y="122" width="26" height="10" fill="%s"/>'
        '<rect x="148" y="122" width="26" height="10" fill="%s"/>'
        '<rect x="90" y="72" width="70" height="46" fill="%s" stroke="%s" stroke-width="2"/>'
        '<line x1="140" y1="90" x2="235" y2="112" stroke="%s" stroke-width="6" stroke-linecap="round"/>'
        '<circle cx="242" cy="115" r="18" fill="none" stroke="%s" stroke-width="3"/>'
        '<line x1="224" y1="115" x2="260" y2="115" stroke="%s" stroke-width="1"/>'
        '<line x1="242" y1="97" x2="242" y2="133" stroke="%s" stroke-width="1"/>'
        '<line x1="112" y1="80" x2="30" y2="42" stroke="%s" stroke-width="5" stroke-linecap="round"/>'
        '<rect x="8" y="30" width="26" height="18" fill="%s"/>'
    ) % (INK, INK, INK, INK, INK, BLUESOFT, BLUE, INK, INK, INK, INK, INK, MID)),
    "komatsu-4100xpc": (200, 120, (
        '<rect x="15" y="108" width="140" height="12" fill="%s"/>'
        '<rect x="60" y="62" width="60" height="42" fill="%s" stroke="%s" stroke-width="2"/>'
        '<line x1="95" y1="62" x2="150" y2="18" stroke="%s" stroke-width="6" stroke-linecap="round"/>'
        '<line x1="150" y1="18" x2="183" y2="72" stroke="%s" stroke-width="5" stroke-linecap="round"/>'
        '<line x1="150" y1="18" x2="185" y2="65" stroke="%s" stroke-width="1.5"/>'
        '<polygon points="176,58 198,58 194,80 180,78" fill="%s"/>'
    ) % (INK, BLUESOFT, BLUE, INK, INK, MID, MID)),
    "bertha-tbm": (230, 88, (
        '<rect x="55" y="25" width="165" height="45" rx="20" fill="%s" stroke="%s" stroke-width="2"/>'
        '<circle cx="55" cy="47" r="38" fill="none" stroke="%s" stroke-width="4"/>'
        '<line x1="55" y1="9" x2="55" y2="85" stroke="%s" stroke-width="1.5"/>'
        '<line x1="17" y1="47" x2="93" y2="47" stroke="%s" stroke-width="1.5"/>'
        '<line x1="29" y1="21" x2="81" y2="73" stroke="%s" stroke-width="1.5"/>'
        '<line x1="29" y1="73" x2="81" y2="21" stroke="%s" stroke-width="1.5"/>'
        '<rect x="205" y="55" width="18" height="18" fill="%s"/>'
    ) % (BLUESOFT, BLUE, INK, INK, INK, INK, INK, MID)),
    "sarens-sgc-250": (170, 248, (
        '<rect x="25" y="228" width="120" height="18" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="18" y="208" width="28" height="20" fill="%s"/>'
        '<rect x="122" y="208" width="28" height="20" fill="%s"/>'
        '<line x1="85" y1="228" x2="140" y2="20" stroke="%s" stroke-width="5" stroke-linecap="round"/>'
        '<line x1="95" y1="200" x2="120" y2="170" stroke="%s" stroke-width="2"/>'
        '<line x1="100" y1="160" x2="122" y2="130" stroke="%s" stroke-width="2"/>'
        '<line x1="105" y1="120" x2="127" y2="90" stroke="%s" stroke-width="2"/>'
        '<line x1="110" y1="80" x2="132" y2="50" stroke="%s" stroke-width="2"/>'
    ) % (BLUESOFT, BLUE, MID, MID, INK, INK, INK, INK, INK)),
    "kalmar-dcg330": (170, 112, (
        '<rect x="50" y="55" width="80" height="35" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="120" y="38" width="26" height="55" fill="%s"/>'
        '<rect x="44" y="14" width="5" height="76" fill="%s"/>'
        '<rect x="55" y="14" width="5" height="76" fill="%s"/>'
        '<rect x="8" y="84" width="42" height="6" fill="%s"/>'
        '<rect x="8" y="92" width="42" height="6" fill="%s"/>'
        '<circle cx="65" cy="100" r="12" fill="%s"/>'
        '<circle cx="112" cy="100" r="12" fill="%s"/>'
    ) % (BLUESOFT, BLUE, MID, INK, INK, INK, INK, INK, INK)),
    "jcb-541-70": (185, 114, (
        '<rect x="58" y="58" width="60" height="32" fill="%s" stroke="%s" stroke-width="2"/>'
        '<circle cx="75" cy="100" r="14" fill="%s"/>'
        '<circle cx="140" cy="100" r="14" fill="%s"/>'
        '<line x1="90" y1="62" x2="162" y2="22" stroke="%s" stroke-width="8" stroke-linecap="round"/>'
        '<rect x="158" y="16" width="22" height="6" fill="%s"/>'
        '<rect x="52" y="34" width="30" height="26" fill="%s" stroke="%s" stroke-width="2"/>'
    ) % (BLUESOFT, BLUE, INK, INK, INK, INK, BLUESOFT, BLUE)),
    "john-deere-x9-1100": (220, 110, (
        '<circle cx="60" cy="90" r="20" fill="%s"/>'
        '<circle cx="180" cy="95" r="13" fill="%s"/>'
        '<rect x="70" y="48" width="130" height="40" fill="%s" stroke="%s" stroke-width="2"/>'
        '<ellipse cx="130" cy="42" rx="45" ry="16" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="8" y="80" width="60" height="12" fill="%s"/>'
        '<line x1="150" y1="55" x2="192" y2="25" stroke="%s" stroke-width="5" stroke-linecap="round"/>'
    ) % (INK, INK, BLUESOFT, BLUE, BLUESOFT, BLUE, MID, INK)),
    "john-deere-9rx": (200, 78, (
        '<rect x="15" y="58" width="60" height="20" fill="%s"/>'
        '<rect x="125" y="58" width="60" height="20" fill="%s"/>'
        '<rect x="50" y="33" width="100" height="30" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="85" y="13" width="35" height="25" fill="%s" stroke="%s" stroke-width="2"/>'
    ) % (INK, INK, BLUESOFT, BLUE, BLUESOFT, BLUE)),
    "john-deere-r4045": (260, 106, (
        '<circle cx="90" cy="90" r="16" fill="%s"/>'
        '<circle cx="170" cy="90" r="16" fill="%s"/>'
        '<rect x="70" y="48" width="120" height="32" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="60" y="52" width="24" height="24" fill="%s"/>'
        '<line x1="0" y1="28" x2="260" y2="28" stroke="%s" stroke-width="3"/>'
        '<line x1="130" y1="48" x2="130" y2="28" stroke="%s" stroke-width="2"/>'
    ) % (INK, INK, BLUESOFT, BLUE, MID, INK, INK)),
    "epiroc-pv351": (140, 186, (
        '<rect x="15" y="172" width="110" height="14" fill="%s"/>'
        '<rect x="30" y="135" width="80" height="37" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="63" y="10" width="14" height="125" fill="%s"/>'
        '<rect x="92" y="115" width="30" height="22" fill="%s"/>'
    ) % (INK, BLUESOFT, BLUE, INK, MID)),
    "ponsse-bear": (230, 105, (
        '<circle cx="40" cy="92" r="13" fill="%s"/>'
        '<circle cx="78" cy="92" r="13" fill="%s"/>'
        '<circle cx="140" cy="92" r="13" fill="%s"/>'
        '<circle cx="178" cy="92" r="13" fill="%s"/>'
        '<rect x="50" y="48" width="120" height="35" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="55" y="26" width="28" height="24" fill="%s" stroke="%s" stroke-width="2"/>'
        '<line x1="150" y1="52" x2="208" y2="28" stroke="%s" stroke-width="6" stroke-linecap="round"/>'
        '<rect x="204" y="12" width="24" height="30" rx="7" fill="%s"/>'
    ) % (INK, INK, INK, INK, BLUESOFT, BLUE, BLUESOFT, BLUE, INK, MID)),
    "konecranes-rtg": (220, 202, (
        '<line x1="20" y1="188" x2="70" y2="18" stroke="%s" stroke-width="7" stroke-linecap="round"/>'
        '<line x1="200" y1="188" x2="150" y2="18" stroke="%s" stroke-width="7" stroke-linecap="round"/>'
        '<rect x="62" y="8" width="96" height="14" fill="%s" stroke="%s" stroke-width="2"/>'
        '<rect x="100" y="26" width="20" height="10" fill="%s"/>'
        '<line x1="110" y1="36" x2="110" y2="55" stroke="%s" stroke-width="2"/>'
        '<rect x="85" y="55" width="50" height="10" fill="%s"/>'
        '<circle cx="24" cy="193" r="9" fill="%s"/>'
        '<circle cx="58" cy="193" r="9" fill="%s"/>'
        '<circle cx="162" cy="193" r="9" fill="%s"/>'
        '<circle cx="196" cy="193" r="9" fill="%s"/>'
    ) % (INK, INK, BLUESOFT, BLUE, MID, INK, MID, INK, INK, INK, INK)),
    "m1150-abv": (190, 82, (
        '<rect x="10" y="70" width="150" height="12" fill="%s"/>'
        '<rect x="35" y="44" width="100" height="30" fill="%s" stroke="%s" stroke-width="2"/>'
        '<polygon points="5,52 28,42 33,74 10,74" fill="%s"/>'
        '<rect x="88" y="26" width="45" height="20" fill="%s"/>'
    ) % (INK, BLUESOFT, BLUE, MID, MID)),
    "spartacus-dredger": (260, 124, (
        '<polygon points="10,92 250,92 235,62 40,62" fill="%s" stroke="%s" stroke-width="2"/>'
        '<line x1="0" y1="97" x2="260" y2="97" stroke="%s" stroke-width="1.5" stroke-dasharray="4,3"/>'
        '<rect x="150" y="35" width="40" height="28" fill="%s" stroke="%s" stroke-width="2"/>'
        '<line x1="190" y1="35" x2="190" y2="6" stroke="%s" stroke-width="4"/>'
        '<line x1="40" y1="62" x2="10" y2="112" stroke="%s" stroke-width="6" stroke-linecap="round"/>'
        '<circle cx="8" cy="114" r="8" fill="%s"/>'
    ) % (BLUESOFT, BLUE, MID, BLUESOFT, BLUE, INK, INK, MID)),
}


# Real photos, sourced only from Wikimedia Commons under a verified free license
# (never manufacturer/stock imagery), one per machine where a genuine match for
# that exact model exists. Deliberately absent for machines with no confirmed match
# rather than substituting a similar-looking machine.
MACHINE_PHOTOS = {
    "caterpillar-d11": {
        "file": "caterpillar-d11.jpg", "author": "Shaun Greiner", "license": "CC BY-SA 2.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "source_url": "https://commons.wikimedia.org/wiki/File:CatD11T.jpg",
        "caption": "A Caterpillar D11T at work.",
    },
    "big-muskie-dragline": {
        "file": "big-muskie-dragline.jpg", "author": "Eric Gunderson", "license": "CC BY-SA 3.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
        "source_url": "https://commons.wikimedia.org/wiki/File:Big_Muskie_Bucket_(Looking_South).JPG",
        "caption": "Big Muskie's bucket — the only piece of the machine that survives, preserved as a monument in Ohio.",
    },
    "bagger-293": {
        "file": "bagger-293.jpg", "author": "Gary Evans", "license": "CC BY-SA 2.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "source_url": "https://commons.wikimedia.org/wiki/File:Bagger_293_Tagebau_Hambach_DE_2017.jpg",
        "caption": "Bagger 293 at the Hambach lignite mine, Germany, 2017.",
    },
    "bertha-tbm": {
        "file": "bertha-tbm.jpg", "author": "SounderBruce", "license": "CC BY-SA 2.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "source_url": "https://commons.wikimedia.org/wiki/File:Bertha_TBM_retrieval_site.jpg",
        "caption": "Bertha's front end during its 2015 retrieval — not mid-bore.",
    },
    "konecranes-rtg": {
        "file": "konecranes-rtg.jpg", "author": "Derek Yu", "license": "CC BY-SA 2.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "source_url": "https://commons.wikimedia.org/wiki/File:RTG_crane_by_Konecranes_SignalPAD.jpg",
        "caption": "A Konecranes RTG at the company's Hyvinkää, Finland test site.",
    },
    "m1150-abv": {
        "file": "m1150-abv.jpg", "author": "Lance Cpl. Brian M. Woodruff, USMC", "license": "Public domain (U.S. federal government work)",
        "license_url": "https://en.wikipedia.org/wiki/Copyright_status_of_works_by_the_federal_government_of_the_United_States",
        "source_url": "https://commons.wikimedia.org/wiki/File:M1_Assault_Breacher_Vehicle.jpg",
        "caption": "An Assault Breacher Vehicle launching a mine-clearing line charge, 2008.",
    },
    "spartacus-dredger": {
        "file": "spartacus-dredger.jpg", "author": "Stephen Cook", "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "source_url": "https://commons.wikimedia.org/wiki/File:Spartacus_cutter_suction_dredger.jpg",
        "caption": "Spartacus during final construction at Royal IHC, Rotterdam.",
    },
}


def photo_block(slug):
    p = MACHINE_PHOTOS.get(slug)
    if not p:
        return ""
    return (
        '<figure class="machine-photo">'
        '<img src="%simg/machines/%s" alt="%s" loading="lazy">'
        '<figcaption>%s Photo: <a href="%s">%s</a>, <a href="%s">%s</a>, via Wikimedia Commons.</figcaption>'
        '</figure>'
        % (BASE, p["file"], esc(p["caption"]), p["caption"], p["source_url"], p["author"], p["license_url"], p["license"])
    )


HUMAN_HEIGHT_M = 1.8


def scale_compare_svg(height_m, label, slug):
    """The machine silhouette is always drawn at a fixed, maximally legible size;
    the human figure is the one that scales, sized by the true ratio between the
    machine's real height and an average adult's height. Equipment size never
    changes from page to page — only how big the human looks next to it does."""
    ratio = height_m / HUMAN_HEIGHT_M
    desc = label or "overall height"

    VB_W, VB_H, GROUND = 340, 220, 196
    X_LEFT, MAX_W, MAX_H = 88, 232, 178

    w_i, h_i, frag = SILHOUETTES[slug]
    s = min(MAX_H / h_i, MAX_W / w_i)
    machine_px_h = h_i * s
    ty = GROUND - machine_px_h
    silhouette = '<g transform="translate(%.2f,%.2f) scale(%.4f)">%s</g>' % (X_LEFT, ty, s, frag)

    px_per_metre = machine_px_h / height_m
    human_h = max(3, HUMAN_HEIGHT_M * px_per_metre)
    human_x = X_LEFT - 34

    human = (
        '<line x1="4" y1="%d" x2="%d" y2="%d" stroke="#c3c9ce" stroke-width="2"/>'
        '<circle cx="%d" cy="%.2f" r="%.2f" fill="%s"/>'
        '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" fill="%s"/>'
        '<text x="%d" y="%d" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="12" font-weight="600" fill="#5b6672">1.8 m</text>'
        % (
            GROUND, VB_W - 6, GROUND,
            human_x, GROUND - human_h * 0.86, max(2, human_h * 0.14), MID,
            human_x - max(3, human_h * 0.13), GROUND - human_h * 0.72, max(6, human_h * 0.27), human_h * 0.72, max(1, human_h * 0.06), MID,
            human_x, GROUND + 16,
        )
    )
    ratio_lbl = (
        '<text x="%.1f" y="18" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="18" font-weight="700" fill="%s">%s×</text>'
        % (X_LEFT + (w_i * s) / 2, BLUE, "{:,.1f}".format(ratio) if ratio < 10 else "{:,.0f}".format(ratio))
    )
    svg = (
        '<svg viewBox="0 0 %d %d" role="img" aria-label="A human figure, drawn to scale, next to this machine\'s silhouette — the machine is %.1f metres tall (%s), about %s times an average adult\'s height.">%s%s%s</svg>'
        % (VB_W, VB_H, height_m, esc(desc), "{:,.1f}".format(ratio), human, silhouette, ratio_lbl)
    )
    caption = (
        '<p class="sc-caption">%s: <strong>%.1f m</strong> — about <strong>%s×</strong> an average adult\'s height (1.8 m). The machine is always drawn at the same size here; the human figure is what actually scales.</p>'
        % (desc[0].upper() + desc[1:], height_m, "{:,.1f}".format(ratio) if ratio < 10 else "{:,.0f}".format(ratio))
    )
    return '<div class="scale-compare">%s%s</div>' % (svg, caption)


def component_list(items):
    lis = "".join(
        '<li><span class="cname">%s</span><span class="cnote">%s</span></li>' % (n, note)
        for n, note in items
    )
    return '<ul class="component-list">%s</ul>' % lis


def concept_grid(principle_links, concepts_by_slug):
    cards = []
    for slug, blurb in principle_links:
        c = concepts_by_slug[slug]
        cards.append(
            '<a class="concept-card" href="%sconcepts/%s/">'
            '<span class="cc-domain">%s</span>'
            '<span class="cc-title">%s</span>'
            '<p class="cc-blurb">%s</p></a>'
            % (BASE, slug, domain_label(c["domain"]), c["title"], blurb)
        )
    return '<div class="concept-grid">%s</div>' % "".join(cards)


def spec_table(rows):
    trs = "".join('<tr><td>%s</td><td>%s</td></tr>' % (k, v) for k, v in rows)
    return '<table class="spec-table">%s</table>' % trs


def example_list(items):
    lis = "".join(
        '<li><span class="ex-name">%s</span><span class="ex-note">%s</span></li>' % (n, note)
        for n, note in items
    )
    return '<ul class="example-list">%s</ul>' % lis


def facts_list(items):
    return '<ul class="facts-list">%s</ul>' % "".join('<li>%s</li>' % f for f in items)


def formula_boxes(formulas):
    boxes = []
    for row in formulas:
        label, expr, note = (row + (None,))[:3] if len(row) < 3 else row
        note_html = '<div class="eq-n">%s</div>' % note if note else ""
        boxes.append(
            '<div class="eq-box"><div class="eq-l">%s</div><div class="eq-b">%s</div>%s</div>'
            % (label, expr, note_html)
        )
    return "".join(boxes)


def category_label(cid):
    return next(c["label"] for c in CATEGORIES if c["id"] == cid)


def domain_label(did):
    return next(d["label"] for d in DOMAINS if d["id"] == did)


HEAD_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Heavy Machinery Encyclopedia</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title} — Heavy Machinery Encyclopedia">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Heavy Machinery Encyclopedia">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Sans+Condensed:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/site.css">
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<header id="site-header"><div class="hdr-inner">
  <a class="brand" href="{base}"><span class="mark">⚙</span> Heavy Machinery Encyclopedia</a>
  <nav class="hdr-nav"></nav>
</div></header>
"""

FOOT_TMPL = """
<footer id="site-footer"><div class="ftr-inner">
  <span>HEAVY MACHINERY ENCYCLOPEDIA — UNDERSTAND THE MACHINE THROUGH THE ENGINEERING</span>
  <span>EDUCATIONAL — SPECIFICATIONS SIMPLIFIED FOR CLARITY, SOURCED FROM MANUFACTURER DATA</span>
</div></footer>
<script type="application/json" id="page-data">{pagedata}</script>
<script src="{base}assets/site.js" defer></script>
</body>
</html>
"""


def render_machine(m, concepts_by_slug):
    cat_label = category_label(m["category"])
    canonical = "%s/machines/%s/" % (SITE_URL, m["slug"])
    breadcrumb_jsonld = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Heavy Machinery Encyclopedia", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": cat_label, "item": "%s/machines/#%s" % (SITE_URL, m["category"])},
            {"@type": "ListItem", "position": 3, "name": m["title"], "item": canonical},
        ],
    }
    tech_jsonld = {"@context": "https://schema.org", "@type": "TechArticle", "headline": m["title"], "description": m["summary"], "isPartOf": {"@type": "WebSite", "name": "Heavy Machinery Encyclopedia", "url": SITE_URL + "/"}}
    jsonld = json.dumps([tech_jsonld, breadcrumb_jsonld])

    head = HEAD_TMPL.format(title=m["title"], description=m["summary"], canonical=canonical, base=BASE, jsonld=jsonld)

    body = []
    body.append('<main>')
    body.append('<div class="crumb"><a href="%s">Home</a> / <a href="%smachines/#%s">%s</a> / %s</div>' % (BASE, BASE, m["category"], cat_label, m["title"]))
    body.append('<section class="hero">')
    body.append('<span class="chip">%s</span>' % cat_label)
    body.append('<h1>%s</h1>' % m["title"])
    body.append('<p class="lede">%s</p>' % m["summary"])
    body.append(stat_row(m["stats"]))
    scale_height_m, scale_label = m["scale"]
    body.append(scale_compare_svg(scale_height_m, scale_label, m["slug"]))
    body.append('</section>')
    photo = photo_block(m["slug"])
    if photo:
        body.append(photo)

    sections = [
        ("overview", "Overview", '<p>%s</p>' % m["summary"]),
        ("purpose", "Purpose", '<p>%s</p>' % m["purpose"]),
        ("history", "Historical Development", '<p>%s</p>' % m["history"]),
        ("components", "Core Components", component_list(m["components"])),
        ("how-it-works", "How It Works", '<p>%s</p>' % m["how_it_works"]),
        ("principles", "Engineering Principles", concept_grid(m["principles"], concepts_by_slug)),
        ("performance", "Performance Characteristics", spec_table(m["performance"])),
        ("examples", "Notable Examples", example_list(m["examples"])),
        ("facts", "Interesting Facts", facts_list(m["facts"])),
        ("related", "Related Machines", '<div id="relatedMachines" class="related-grid"></div>'),
    ]
    for i, (sec_id, title, inner) in enumerate(sections, 1):
        body.append('<section class="block" id="%s"><h2><span class="n">%02d</span>%s</h2>%s</section>' % (sec_id, i, title, inner))
    body.append('</main>')

    pagedata = json.dumps({"type": "machine", "slug": m["slug"], "category": m["category"], "principles": [p[0] for p in m["principles"]]})
    foot = FOOT_TMPL.format(base=BASE, pagedata=pagedata)
    return head + "\n".join(body) + foot


def render_concept(c):
    dom_label = domain_label(c["domain"])
    canonical = "%s/concepts/%s/" % (SITE_URL, c["slug"])
    breadcrumb_jsonld = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Heavy Machinery Encyclopedia", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": dom_label, "item": "%s/concepts/#%s" % (SITE_URL, c["domain"])},
            {"@type": "ListItem", "position": 3, "name": c["title"], "item": canonical},
        ],
    }
    tech_jsonld = {"@context": "https://schema.org", "@type": "TechArticle", "headline": c["title"], "description": c["definition"], "isPartOf": {"@type": "WebSite", "name": "Heavy Machinery Encyclopedia", "url": SITE_URL + "/"}}
    jsonld = json.dumps([tech_jsonld, breadcrumb_jsonld])

    head = HEAD_TMPL.format(title=c["title"], description=c["definition"], canonical=canonical, base=BASE, jsonld=jsonld)

    body = []
    body.append('<main>')
    body.append('<div class="crumb"><a href="%s">Home</a> / <a href="%sconcepts/#%s">%s</a> / %s</div>' % (BASE, BASE, c["domain"], dom_label, c["title"]))
    body.append('<section class="hero">')
    body.append('<span class="chip domain">%s</span>' % dom_label)
    body.append('<h1>%s</h1>' % c["title"])
    body.append('<p class="lede">%s</p>' % c["definition"])
    body.append(stat_row(c["stats"]))
    body.append('</section>')

    sections = [
        ("definition", "Definition", '<p>%s</p>' % c["definition"]),
        ("principle", "Physical Principle", '<p>%s</p>' % c["principle"]),
        ("math", "Mathematical Foundation", formula_boxes(c["formulas"])),
    ]
    interactive = c.get("interactive")
    if interactive in INTERACTIVE_HTML:
        sections.append(("interactive", "Interactive Diagram — " + INTERACTIVE_TITLE[interactive], INTERACTIVE_HTML[interactive]))
    sections += [
        ("facts", "Interesting Facts", facts_list(c["facts"])),
        ("applications", "Real-World Applications", '<div id="realWorldApplications" class="related-grid"></div>'),
        ("related", "Related Concepts", '<div id="relatedConcepts" class="related-grid"></div>'),
    ]
    for i, (sec_id, title, inner) in enumerate(sections, 1):
        body.append('<section class="block" id="%s"><h2><span class="n">%02d</span>%s</h2>%s</section>' % (sec_id, i, title, inner))
    body.append('</main>')

    pagedata = json.dumps({"type": "concept", "slug": c["slug"], "domain": c["domain"], "relatedConcepts": c.get("related_concepts", [])})
    interactive_js = INTERACTIVE_JS.get(interactive, "")
    foot = FOOT_TMPL.format(base=BASE, pagedata=pagedata)
    if interactive_js:
        foot = foot.replace("</body>", interactive_js + "\n</body>")
    return head + "\n".join(body) + foot


# ------------------------------------------------------------------
# Bespoke interactive primitives (Sheet 04, primitives 2 & 4)
# ------------------------------------------------------------------
GEAR_SIM_HTML = """
<p>Set the tooth count on the driving gear (A) and the driven gear (B) and watch the ratio, output speed, and torque multiplication update live.</p>
<div class="sim-panel">
  <div class="viewport"><svg id="gearSvg" viewBox="0 0 300 300" width="100%" height="100%" role="img" aria-label="Two meshed gears rotating according to the chosen tooth counts"></svg></div>
  <div class="sim-row"><span>TEETH ON A (driving)</span><span class="mono" id="teethAVal">20</span></div>
  <input id="teethASlider" type="range" min="8" max="60" step="1" value="20">
  <div class="sim-row"><span>TEETH ON B (driven)</span><span class="mono" id="teethBVal">40</span></div>
  <input id="teethBSlider" type="range" min="8" max="60" step="1" value="40">
  <div class="sim-readout" id="gearReadout"></div>
  <p class="sim-note">Input speed fixed at 1,000 RPM on gear A.</p>
</div>"""

GEAR_SIM_JS = """
<script>
(function(){
  var a = document.getElementById('teethASlider'), b = document.getElementById('teethBSlider');
  var aVal = document.getElementById('teethAVal'), bVal = document.getElementById('teethBVal');
  var svg = document.getElementById('gearSvg'), readout = document.getElementById('gearReadout');
  if(!a||!b||!svg) return;
  function ns(tag,attrs){ var el=document.createElementNS('http://www.w3.org/2000/svg',tag); for(var k in attrs) el.setAttribute(k,attrs[k]); return el; }
  function gearPath(cx, cy, r, teeth){
    var toothDepth = r*0.14, pts=[];
    for(var i=0;i<teeth;i++){
      var a0 = (i/teeth)*Math.PI*2, a1=((i+0.5)/teeth)*Math.PI*2, a2=((i+1)/teeth)*Math.PI*2;
      pts.push([cx+Math.cos(a0)*r, cy+Math.sin(a0)*r]);
      pts.push([cx+Math.cos(a1)*(r+toothDepth), cy+Math.sin(a1)*(r+toothDepth)]);
      pts.push([cx+Math.cos(a2)*r, cy+Math.sin(a2)*r]);
    }
    return 'M'+pts.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1);}).join(' L')+' Z';
  }
  function draw(){
    var ta=parseInt(a.value,10), tb=parseInt(b.value,10);
    aVal.textContent=ta; bVal.textContent=tb;
    var ratio = tb/ta;
    var rpmA=1000, rpmB=rpmA/ratio;
    var ra = 30+ta*1.3, rb = 30+tb*1.3;
    var cx1=110, cy=150, cx2=cx1+ra+rb;
    if(cx2>270){ var scale=(270-cx1)/(ra+rb); ra*=scale; rb*=scale; cx2=cx1+ra+rb; }
    svg.innerHTML='';
    svg.setAttribute('viewBox','0 0 '+(cx2+ra+20)+' 300');
    var g1=ns('path',{d:gearPath(cx1,cy,ra,ta), fill:'#e8edfb', stroke:'#2454c7', 'stroke-width':1.5});
    var g2=ns('path',{d:gearPath(cx2,cy,rb,tb), fill:'#f7e8df', stroke:'#c1541d', 'stroke-width':1.5});
    svg.appendChild(g1); svg.appendChild(g2);
    svg.appendChild(ns('circle',{cx:cx1,cy:cy,r:4,fill:'#151a1f'}));
    svg.appendChild(ns('circle',{cx:cx2,cy:cy,r:4,fill:'#151a1f'}));
    var t1=ns('text',{x:cx1,y:cy+5,'text-anchor':'middle','font-family':'IBM Plex Mono, monospace','font-size':'11','font-weight':'700',fill:'#2454c7'}); t1.textContent='A'; svg.appendChild(t1);
    var t2=ns('text',{x:cx2,y:cy+5,'text-anchor':'middle','font-family':'IBM Plex Mono, monospace','font-size':'11','font-weight':'700',fill:'#c1541d'}); t2.textContent='B'; svg.appendChild(t2);
    var dur1=(2/(rpmA/60)).toFixed(2), dur2=(2/(rpmB/60)).toFixed(2);
    g1.style.transformOrigin=cx1+'px '+cy+'px'; g1.style.animation='spin '+dur1+'s linear infinite';
    g2.style.transformOrigin=cx2+'px '+cy+'px'; g2.style.animation='spin-rev '+dur2+'s linear infinite';
    var cells=[
      ['GEAR RATIO', ratio.toFixed(2)+' : 1'],
      ['OUTPUT SPEED (B)', rpmB.toFixed(0)+' RPM'],
      ['TORQUE MULTIPLIER', ratio.toFixed(2)+'×']
    ];
    readout.innerHTML = cells.map(function(c){return '<div class="cell"><span class="l">'+c[0]+'</span><span class="v">'+c[1]+'</span></div>';}).join('');
  }
  var style=document.createElement('style');
  style.textContent='@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}@keyframes spin-rev{from{transform:rotate(0deg)}to{transform:rotate(-360deg)}}@media (prefers-reduced-motion:reduce){#gearSvg path{animation:none!important;}}';
  document.head.appendChild(style);
  a.addEventListener('input',draw); b.addEventListener('input',draw);
  draw();
})();
</script>"""

HYDRAULIC_SIM_HTML = """
<p>Set the input piston force and the ratio between the two piston areas to see how much force the output piston delivers.</p>
<div class="sim-panel">
  <div class="viewport"><svg id="hydSvg" viewBox="0 0 340 220" width="100%" height="100%" role="img" aria-label="Two connected hydraulic cylinders of different piston area"></svg></div>
  <div class="sim-row"><span>INPUT FORCE</span><span class="mono" id="hydForceVal">50 kg</span></div>
  <input id="hydForceSlider" type="range" min="5" max="200" step="1" value="50">
  <div class="sim-row"><span>OUTPUT / INPUT AREA RATIO</span><span class="mono" id="hydRatioVal">10 : 1</span></div>
  <input id="hydRatioSlider" type="range" min="1" max="30" step="1" value="10">
  <div class="sim-readout" id="hydReadout"></div>
  <p class="sim-note">Pressure is transmitted equally throughout the fluid — only the piston areas differ.</p>
</div>"""

HYDRAULIC_SIM_JS = """
<script>
(function(){
  var f = document.getElementById('hydForceSlider'), r = document.getElementById('hydRatioSlider');
  var fVal = document.getElementById('hydForceVal'), rVal = document.getElementById('hydRatioVal');
  var svg = document.getElementById('hydSvg'), readout = document.getElementById('hydReadout');
  if(!f||!r||!svg) return;
  function ns(tag,attrs){ var el=document.createElementNS('http://www.w3.org/2000/svg',tag); for(var k in attrs) el.setAttribute(k,attrs[k]); return el; }
  function draw(){
    var force=parseFloat(f.value), ratio=parseFloat(r.value);
    fVal.textContent=force+' kg'; rVal.textContent=ratio+' : 1';
    var outForce = force*ratio;
    var rIn=14, rOut=Math.min(70, rIn*Math.sqrt(ratio));
    svg.innerHTML='';
    svg.appendChild(ns('rect',{x:10,y:170,width:320,height:10,fill:'#c3c9ce'}));
    svg.appendChild(ns('rect',{x:40-rIn,y:70,width:rIn*2,height:100,fill:'none',stroke:'#151a1f','stroke-width':2}));
    svg.appendChild(ns('rect',{x:40-rIn+2,y:170-6,width:rIn*2-4,height:6,fill:'#2454c7'}));
    var pistonInY = 170-6-18;
    svg.appendChild(ns('rect',{x:40-rIn+1,y:pistonInY,width:rIn*2-2,height:10,fill:'#151a1f'}));
    var cx2=250;
    svg.appendChild(ns('rect',{x:cx2-rOut,y:170-Math.max(20,rOut*1.3),width:rOut*2,height:Math.max(20,rOut*1.3),fill:'none',stroke:'#151a1f','stroke-width':2}));
    var outH = Math.max(20, rOut*1.3);
    svg.appendChild(ns('rect',{x:cx2-rOut+2,y:170-6,width:rOut*2-4,height:6,fill:'#c1541d'}));
    var pistonOutY = 170-6-Math.min(outH-10, 18+ratio*1.2);
    svg.appendChild(ns('rect',{x:cx2-rOut+1,y:Math.max(170-outH+2,pistonOutY),width:rOut*2-2,height:10,fill:'#151a1f'}));
    svg.appendChild(ns('line',{x1:40,y1:180,x2:cx2,y2:180,stroke:'#151a1f','stroke-width':2}));
    var lbl1=ns('text',{x:40,y:60,'text-anchor':'middle','font-family':'IBM Plex Mono, monospace','font-size':'10',fill:'#2454c7'}); lbl1.textContent='INPUT'; svg.appendChild(lbl1);
    var lbl2=ns('text',{x:cx2,y:Math.max(30,170-outH-8),'text-anchor':'middle','font-family':'IBM Plex Mono, monospace','font-size':'10',fill:'#c1541d'}); lbl2.textContent='OUTPUT'; svg.appendChild(lbl2);
    var cells=[
      ['INPUT FORCE', force+' kg'],
      ['AREA RATIO', ratio+' : 1'],
      ['OUTPUT FORCE', outForce.toLocaleString()+' kg']
    ];
    readout.innerHTML = cells.map(function(c){return '<div class="cell"><span class="l">'+c[0]+'</span><span class="v">'+c[1]+'</span></div>';}).join('');
  }
  f.addEventListener('input',draw); r.addEventListener('input',draw);
  draw();
})();
</script>"""

TORQUE_SIM_HTML = """
<p>Slide the applied force and the lever-arm length to see how the torque at the pivot responds.</p>
<div class="sim-panel">
  <div class="viewport"><svg id="trqSvg" viewBox="0 0 300 220" width="100%" height="100%" role="img" aria-label="A force applied at a distance from a pivot, producing torque"></svg></div>
  <div class="sim-row"><span>FORCE</span><span class="mono" id="trqForceVal">200 N</span></div>
  <input id="trqForceSlider" type="range" min="20" max="500" step="10" value="200">
  <div class="sim-row"><span>LEVER ARM</span><span class="mono" id="trqArmVal">1.0 m</span></div>
  <input id="trqArmSlider" type="range" min="0.2" max="3" step="0.1" value="1.0">
  <div class="sim-readout" id="trqReadout"></div>
  <p class="sim-note">τ = F × r — the same force produces more torque the farther it acts from the pivot.</p>
</div>"""

TORQUE_SIM_JS = """
<script>
(function(){
  var f=document.getElementById('trqForceSlider'), r=document.getElementById('trqArmSlider');
  var fVal=document.getElementById('trqForceVal'), rVal=document.getElementById('trqArmVal');
  var svg=document.getElementById('trqSvg'), readout=document.getElementById('trqReadout');
  if(!f||!r||!svg) return;
  function ns(tag,attrs){ var el=document.createElementNS('http://www.w3.org/2000/svg',tag); for(var k in attrs) el.setAttribute(k,attrs[k]); return el; }
  function draw(){
    var force=parseFloat(f.value), arm=parseFloat(r.value);
    fVal.textContent=force+' N'; rVal.textContent=arm.toFixed(1)+' m';
    var torque=force*arm;
    var px=40, py=180, scale=70;
    var ex=px+arm*scale, ey=py;
    svg.innerHTML='';
    svg.appendChild(ns('polygon',{points:(px-10)+','+(py+18)+' '+(px+10)+','+(py+18)+' '+px+','+py, fill:'#151a1f'}));
    svg.appendChild(ns('line',{x1:px,y1:py,x2:ex,y2:ey, stroke:'#2454c7','stroke-width':6,'stroke-linecap':'round'}));
    var arrowLen=Math.min(110, 20+force/6);
    svg.appendChild(ns('line',{x1:ex,y1:ey-arrowLen,x2:ex,y2:ey-6, stroke:'#c1541d','stroke-width':4}));
    svg.appendChild(ns('polygon',{points:(ex-7)+','+(ey-16)+' '+(ex+7)+','+(ey-16)+' '+ex+','+(ey-2), fill:'#c1541d'}));
    var lbl=ns('text',{x:ex,y:Math.max(16,ey-arrowLen-8),'text-anchor':'middle','font-family':'IBM Plex Mono, monospace','font-size':'11','font-weight':'700',fill:'#c1541d'}); lbl.textContent='F'; svg.appendChild(lbl);
    var cells=[['FORCE',force+' N'],['LEVER ARM',arm.toFixed(1)+' m'],['TORQUE',torque.toFixed(0)+' N·m']];
    readout.innerHTML=cells.map(function(c){return '<div class="cell"><span class="l">'+c[0]+'</span><span class="v">'+c[1]+'</span></div>';}).join('');
  }
  f.addEventListener('input',draw); r.addEventListener('input',draw);
  draw();
})();
</script>"""

MA_SIM_HTML = """
<p>Slide the fulcrum position between a fixed effort and a fixed 500&nbsp;kg load to see how mechanical advantage — and the effort actually needed — changes.</p>
<div class="sim-panel">
  <div class="viewport"><svg id="maSvg" viewBox="0 0 300 200" width="100%" height="100%" role="img" aria-label="A lever balancing an effort force against a fixed load, with a movable fulcrum"></svg></div>
  <div class="sim-row"><span>FULCRUM POSITION (from effort side)</span><span class="mono" id="maFulcrumVal">30%</span></div>
  <input id="maFulcrumSlider" type="range" min="10" max="90" step="1" value="30">
  <div class="sim-readout" id="maReadout"></div>
  <p class="sim-note">Load fixed at 500 kg. Moving the fulcrum toward the load shortens the load arm and raises mechanical advantage.</p>
</div>"""

MA_SIM_JS = """
<script>
(function(){
  var s=document.getElementById('maFulcrumSlider'), val=document.getElementById('maFulcrumVal');
  var svg=document.getElementById('maSvg'), readout=document.getElementById('maReadout');
  if(!s||!svg) return;
  function ns(tag,attrs){ var el=document.createElementNS('http://www.w3.org/2000/svg',tag); for(var k in attrs) el.setAttribute(k,attrs[k]); return el; }
  var load=500, x0=30, x1=270, beamRealM=2.0, y=130;
  function draw(){
    var pct=parseInt(s.value,10); val.textContent=pct+'%';
    var fx=x0+(x1-x0)*(pct/100);
    var effortPx=fx-x0, loadPx=x1-fx;
    var mPerPx=beamRealM/(x1-x0);
    var effortArm=effortPx*mPerPx, loadArm=loadPx*mPerPx;
    var ma=effortArm/loadArm, effortNeeded=load/ma;
    svg.innerHTML='';
    svg.appendChild(ns('line',{x1:x0,y1:y,x2:x1,y2:y, stroke:'#2454c7','stroke-width':6,'stroke-linecap':'round'}));
    svg.appendChild(ns('polygon',{points:(fx-12)+','+(y+22)+' '+(fx+12)+','+(y+22)+' '+fx+','+y, fill:'#151a1f'}));
    svg.appendChild(ns('circle',{cx:x0,cy:y-24,r:12,fill:'none',stroke:'#c1541d','stroke-width':3}));
    svg.appendChild(ns('line',{x1:x0,y1:y-12,x2:x0,y2:y, stroke:'#c1541d','stroke-width':3}));
    svg.appendChild(ns('rect',{x:x1-16,y:y-34,width:32,height:32,fill:'#5b6672'}));
    var t1=ns('text',{x:x0,y:y-46,'text-anchor':'middle','font-family':'IBM Plex Mono, monospace','font-size':'10',fill:'#c1541d'}); t1.textContent='EFFORT'; svg.appendChild(t1);
    var t2=ns('text',{x:x1,y:y-42,'text-anchor':'middle','font-family':'IBM Plex Mono, monospace','font-size':'10',fill:'#5b6672'}); t2.textContent='LOAD'; svg.appendChild(t2);
    var cells=[['EFFORT ARM',effortArm.toFixed(2)+' m'],['LOAD ARM',loadArm.toFixed(2)+' m'],['MECHANICAL ADVANTAGE',ma.toFixed(2)+' : 1'],['EFFORT NEEDED',effortNeeded.toFixed(0)+' kg']];
    readout.innerHTML=cells.map(function(c){return '<div class="cell"><span class="l">'+c[0]+'</span><span class="v">'+c[1]+'</span></div>';}).join('');
  }
  s.addEventListener('input',draw);
  draw();
})();
</script>"""

PLANETARY_SIM_HTML = """
<p>Choose which member is held fixed and watch the other two rotate at the resulting speed — the same three gears, three different outcomes.</p>
<div class="sim-panel">
  <div class="viewport"><svg id="planetSvg" viewBox="0 0 300 300" width="100%" height="100%" role="img" aria-label="A planetary gearset: sun, planets, and ring, with one member held fixed"></svg></div>
  <div class="sim-btn-row">
    <button type="button" class="sim-btn active" data-mode="ring">Ring Fixed</button>
    <button type="button" class="sim-btn" data-mode="carrier">Carrier Fixed</button>
    <button type="button" class="sim-btn" data-mode="sun">Sun Fixed</button>
  </div>
  <div class="sim-readout" id="planetReadout"></div>
  <p class="sim-note">Sun = 24 teeth, ring = 72 teeth throughout — only which member is held changes the outcome.</p>
</div>"""

PLANETARY_SIM_JS = """
<script>
(function(){
  var svg=document.getElementById('planetSvg'), readout=document.getElementById('planetReadout');
  var btns=document.querySelectorAll('.sim-btn[data-mode]');
  if(!svg||!btns.length) return;
  function ns(tag,attrs){ var el=document.createElementNS('http://www.w3.org/2000/svg',tag); for(var k in attrs) el.setAttribute(k,attrs[k]); return el; }
  var Nsun=24, Nring=72, cx=150, cy=150, mode='ring';
  var style=document.createElement('style');
  style.textContent='@keyframes pspin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}@keyframes pspin-rev{from{transform:rotate(0deg)}to{transform:rotate(-360deg)}}@media (prefers-reduced-motion:reduce){#planetSvg g{animation:none!important;}}';
  document.head.appendChild(style);
  function outcome(){
    if(mode==='ring') return {sun:1000, carrier:1000/(1+Nring/Nsun), ring:0, fixed:'RING', out:'CARRIER', ratio:1/(1+Nring/Nsun)};
    if(mode==='carrier') return {sun:1000, carrier:0, ring:-1000*(Nsun/Nring), fixed:'CARRIER', out:'RING', ratio:-(Nsun/Nring)};
    return {sun:0, carrier:1000, ring:1000*((Nring+Nsun)/Nring), fixed:'SUN', out:'RING', ratio:(Nring+Nsun)/Nring};
  }
  function spinStyle(rpm){
    if(Math.abs(rpm)<1) return 'animation:none;';
    var dur=(60/Math.abs(rpm*0.15)).toFixed(1);
    return 'transform-origin:'+cx+'px '+cy+'px; animation:'+(rpm>0?'pspin':'pspin-rev')+' '+dur+'s linear infinite;';
  }
  function draw(){
    var o=outcome();
    svg.innerHTML='';
    var ring=ns('g',{style:spinStyle(o.ring)});
    ring.appendChild(ns('circle',{cx:cx,cy:cy,r:110,fill:'none',stroke:'#c1541d','stroke-width':6}));
    ring.appendChild(ns('line',{x1:cx,y1:cy-110,x2:cx,y2:cy-98,stroke:'#c1541d','stroke-width':4}));
    svg.appendChild(ring);
    var carrier=ns('g',{style:spinStyle(o.carrier)});
    for(var i=0;i<3;i++){
      var ang=(i/3)*Math.PI*2, px=cx+Math.cos(ang)*70, py=cy+Math.sin(ang)*70;
      carrier.appendChild(ns('line',{x1:cx,y1:cy,x2:px,y2:py,stroke:'#8a92a0','stroke-width':2}));
      carrier.appendChild(ns('circle',{cx:px,cy:py,r:16,fill:'#f7e8df',stroke:'#c1541d','stroke-width':1.5}));
    }
    svg.appendChild(carrier);
    var sun=ns('g',{style:spinStyle(o.sun)});
    sun.appendChild(ns('circle',{cx:cx,cy:cy,r:34,fill:'#e8edfb',stroke:'#2454c7','stroke-width':1.5}));
    sun.appendChild(ns('line',{x1:cx,y1:cy,x2:cx,y2:cy-34,stroke:'#2454c7','stroke-width':3}));
    svg.appendChild(sun);
    var cells=[['FIXED MEMBER',o.fixed],['SUN RPM',o.sun.toFixed(0)],['CARRIER RPM',o.carrier.toFixed(0)],['RING RPM',o.ring.toFixed(0)]];
    readout.innerHTML=cells.map(function(c){return '<div class="cell"><span class="l">'+c[0]+'</span><span class="v">'+c[1]+'</span></div>';}).join('');
  }
  btns.forEach(function(b){
    b.addEventListener('click',function(){
      btns.forEach(function(x){x.classList.remove('active');});
      b.classList.add('active');
      mode=b.getAttribute('data-mode');
      draw();
    });
  });
  draw();
})();
</script>"""

CYLINDER_SIM_HTML = """
<p>Set the cylinder's bore and the pump's flow rate at a fixed 250 bar working pressure to see the force it pushes with, and how fast the rod extends.</p>
<div class="sim-panel">
  <div class="viewport"><svg id="cylSvg" viewBox="0 0 300 180" width="100%" height="100%" role="img" aria-label="A hydraulic cylinder extending, driven by pressurised flow"></svg></div>
  <div class="sim-row"><span>BORE DIAMETER</span><span class="mono" id="cylBoreVal">100 mm</span></div>
  <input id="cylBoreSlider" type="range" min="50" max="300" step="5" value="100">
  <div class="sim-row"><span>PUMP FLOW RATE</span><span class="mono" id="cylFlowVal">80 L/min</span></div>
  <input id="cylFlowSlider" type="range" min="10" max="400" step="5" value="80">
  <div class="sim-readout" id="cylReadout"></div>
  <p class="sim-note">Working pressure fixed at 250 bar. Animation speed is illustrative, not real-time.</p>
</div>"""

CYLINDER_SIM_JS = """
<script>
(function(){
  var bore=document.getElementById('cylBoreSlider'), flow=document.getElementById('cylFlowSlider');
  var boreVal=document.getElementById('cylBoreVal'), flowVal=document.getElementById('cylFlowVal');
  var svg=document.getElementById('cylSvg'), readout=document.getElementById('cylReadout');
  if(!bore||!flow||!svg) return;
  function ns(tag,attrs){ var el=document.createElementNS('http://www.w3.org/2000/svg',tag); for(var k in attrs) el.setAttribute(k,attrs[k]); return el; }
  var P=25000000, strokePx=120, rodEl=null;
  var style=document.createElement('style');
  document.head.appendChild(style);
  function draw(){
    var d=parseFloat(bore.value), q=parseFloat(flow.value);
    boreVal.textContent=d+' mm'; flowVal.textContent=q+' L/min';
    var A=Math.PI*Math.pow(d/2000,2);
    var F=P*A, tonnes=F/9810, kN=F/1000;
    var flowM3s=(q/1000)/60, v=flowM3s/A;
    var periodS=Math.max(0.5,Math.min(4,4/(0.2+v)));
    style.textContent='@keyframes cylext{0%{transform:translateX(0)}50%{transform:translateX('+strokePx+'px)}100%{transform:translateX(0)}}@media (prefers-reduced-motion:reduce){#cylRod{animation:none!important;}}';
    var bodyH=20+d*0.3;
    svg.innerHTML='';
    svg.appendChild(ns('rect',{x:20,y:90-bodyH/2,width:70,height:bodyH,fill:'none',stroke:'#151a1f','stroke-width':2}));
    var rodGroup=ns('g',{id:'cylRod',style:'animation:cylext '+periodS.toFixed(2)+'s ease-in-out infinite;'});
    rodGroup.appendChild(ns('rect',{x:82,y:90-6,width:180,height:12,fill:'#2454c7'}));
    rodGroup.appendChild(ns('rect',{x:250,y:90-18,width:14,height:36,fill:'#151a1f'}));
    svg.appendChild(rodGroup);
    var lbl=ns('text',{x:55,y:90+bodyH/2+18,'text-anchor':'middle','font-family':'IBM Plex Mono, monospace','font-size':'10',fill:'#5b6672'}); lbl.textContent='BORE '+d+' mm'; svg.appendChild(lbl);
    var cells=[['BORE',d+' mm'],['FLOW',q+' L/min'],['FORCE',kN.toFixed(0)+' kN ('+tonnes.toFixed(1)+' t)'],['ROD SPEED',(v*1000).toFixed(0)+' mm/s']];
    readout.innerHTML=cells.map(function(c){return '<div class="cell"><span class="l">'+c[0]+'</span><span class="v">'+c[1]+'</span></div>';}).join('');
  }
  bore.addEventListener('input',draw); flow.addEventListener('input',draw);
  draw();
})();
</script>"""

FOURSTROKE_SIM_HTML = """
<p>Press play to step through one full four-stroke cycle — intake, compression, power, exhaust — two crankshaft revolutions per cycle.</p>
<div class="sim-panel">
  <div class="viewport"><svg id="fsSvg" viewBox="0 0 200 260" width="100%" height="100%" role="img" aria-label="A piston moving through the four-stroke diesel cycle"></svg></div>
  <div class="sim-btn-row"><button type="button" class="sim-btn" id="fsPlayBtn">▶ Play</button></div>
  <div class="sim-row"><span>CYCLE SPEED</span><span class="mono" id="fsSpeedVal">3×</span></div>
  <input id="fsSpeedSlider" type="range" min="1" max="8" step="1" value="3">
  <div class="sim-readout" id="fsReadout"></div>
  <p class="sim-note">Piston motion is simplified for clarity, not exact crank geometry.</p>
</div>"""

FOURSTROKE_SIM_JS = """
<script>
(function(){
  var svg=document.getElementById('fsSvg'), playBtn=document.getElementById('fsPlayBtn');
  var speed=document.getElementById('fsSpeedSlider'), speedVal=document.getElementById('fsSpeedVal'), readout=document.getElementById('fsReadout');
  if(!svg||!playBtn) return;
  function ns(tag,attrs){ var el=document.createElementNS('http://www.w3.org/2000/svg',tag); for(var k in attrs) el.setAttribute(k,attrs[k]); return el; }
  var angle=0, running=false, lastT=null;
  var stages=['INTAKE','COMPRESSION','POWER','EXHAUST'];
  var colors=['#2454c7','#5b6672','#c1541d','#8a92a0'];
  function draw(){
    var stageIdx=Math.floor((angle%720)/180);
    var pistonY=60+ (1-Math.cos(angle*Math.PI/180))*40;
    svg.innerHTML='';
    svg.appendChild(ns('rect',{x:60,y:20,width:80,height:160,fill:'none',stroke:'#151a1f','stroke-width':2}));
    var intakeOpen=stageIdx===0, exhaustOpen=stageIdx===3;
    svg.appendChild(ns('rect',{x:66,y:14,width:20,height:10,fill:intakeOpen?'#2454c7':'#c3c9ce'}));
    svg.appendChild(ns('rect',{x:114,y:14,width:20,height:10,fill:exhaustOpen?'#c1541d':'#c3c9ce'}));
    if(stageIdx===2 && (angle%720)<380){
      svg.appendChild(ns('circle',{cx:100,cy:30,r:5,fill:'#c1541d'}));
    }
    svg.appendChild(ns('rect',{x:65,y:pistonY,width:70,height:28,fill:colors[stageIdx]}));
    svg.appendChild(ns('line',{x1:100,y1:pistonY+28,x2:100,y2:220,stroke:'#151a1f','stroke-width':4}));
    svg.appendChild(ns('circle',{cx:100,cy:220,r:22,fill:'none',stroke:'#151a1f','stroke-width':3}));
    var crankX=100+22*Math.cos(angle*Math.PI/180), crankY=220+22*Math.sin(angle*Math.PI/180);
    svg.appendChild(ns('circle',{cx:crankX,cy:crankY,r:5,fill:'#151a1f'}));
    var lbl=ns('text',{x:100,y:250,'text-anchor':'middle','font-family':'IBM Plex Mono, monospace','font-size':'13','font-weight':'700',fill:colors[stageIdx]}); lbl.textContent=stages[stageIdx]; svg.appendChild(lbl);
    if(readout) readout.innerHTML='<div class="cell"><span class="l">STAGE</span><span class="v">'+stages[stageIdx]+'</span></div><div class="cell"><span class="l">CRANK ANGLE</span><span class="v">'+Math.round(angle%720)+'°</span></div>';
  }
  function frame(t){
    if(!running) return;
    if(lastT!=null){
      var dt=(t-lastT)/1000;
      angle=(angle+dt*parseFloat(speed.value)*90)%720;
    }
    lastT=t;
    draw();
    requestAnimationFrame(frame);
  }
  playBtn.addEventListener('click',function(){
    running=!running;
    playBtn.textContent=running?'⏸ Pause':'▶ Play';
    if(running){ lastT=null; requestAnimationFrame(frame); }
  });
  speed.addEventListener('input',function(){ speedVal.textContent=speed.value+'×'; });
  draw();
})();
</script>"""

TCONV_SIM_HTML = """
<p>Slide the turbine-to-impeller speed ratio to see torque multiplication fall from its peak near stall to 1:1 once both sides spin together.</p>
<div class="sim-panel">
  <div class="viewport"><svg id="tcSvg" viewBox="0 0 300 220" width="100%" height="100%" role="img" aria-label="A torque-multiplication curve against turbine speed ratio, with a marker at the current point"></svg></div>
  <div class="sim-row"><span>SPEED RATIO (turbine / impeller)</span><span class="mono" id="tcRatioVal">0.20</span></div>
  <input id="tcRatioSlider" type="range" min="0" max="100" step="1" value="20">
  <div class="sim-readout" id="tcReadout"></div>
  <p class="sim-note">Input torque fixed at 500 N·m. Multiplication tapers to 1:1 once impeller and turbine converge — the coupling point.</p>
</div>"""

TCONV_SIM_JS = """
<script>
(function(){
  var s=document.getElementById('tcRatioSlider'), val=document.getElementById('tcRatioVal');
  var svg=document.getElementById('tcSvg'), readout=document.getElementById('tcReadout');
  if(!s||!svg) return;
  function ns(tag,attrs){ var el=document.createElementNS('http://www.w3.org/2000/svg',tag); for(var k in attrs) el.setAttribute(k,attrs[k]); return el; }
  function tr(ratio){ return Math.max(1, 2-1.111*ratio); }
  var x0=30,x1=270,y0=190,y1=40;
  function pt(ratio){ var t=tr(ratio); return [x0+ratio*(x1-x0), y0-((t-1)/1)*(y0-y1)]; }
  function draw(){
    var ratio=parseInt(s.value,10)/100; val.textContent=ratio.toFixed(2);
    var t=tr(ratio), outT=500*t;
    svg.innerHTML='';
    svg.appendChild(ns('line',{x1:x0,y1:y0,x2:x1,y2:y0,stroke:'#c3c9ce','stroke-width':2}));
    svg.appendChild(ns('line',{x1:x0,y1:y0,x2:x0,y2:y1,stroke:'#c3c9ce','stroke-width':2}));
    var d='M', pts=[];
    for(var i=0;i<=20;i++){ var p=pt(i/20); pts.push(p[0].toFixed(1)+','+p[1].toFixed(1)); }
    svg.appendChild(ns('path',{d:'M'+pts.join(' L'), fill:'none', stroke:'#2454c7','stroke-width':2.5}));
    var cur=pt(ratio);
    svg.appendChild(ns('circle',{cx:cur[0],cy:cur[1],r:6,fill:'#c1541d'}));
    var lbl1=ns('text',{x:x0-6,y:y1-4,'text-anchor':'start','font-family':'IBM Plex Mono, monospace','font-size':'9',fill:'#8a92a0'}); lbl1.textContent='2.0×'; svg.appendChild(lbl1);
    var lbl2=ns('text',{x:x0-6,y:y0+4,'text-anchor':'start','font-family':'IBM Plex Mono, monospace','font-size':'9',fill:'#8a92a0'}); lbl2.textContent='1.0×'; svg.appendChild(lbl2);
    var cells=[['SPEED RATIO',ratio.toFixed(2)],['TORQUE MULTIPLIER',t.toFixed(2)+'×'],['OUTPUT TORQUE',outT.toFixed(0)+' N·m']];
    readout.innerHTML=cells.map(function(c){return '<div class="cell"><span class="l">'+c[0]+'</span><span class="v">'+c[1]+'</span></div>';}).join('');
  }
  s.addEventListener('input',draw);
  draw();
})();
</script>"""

FINALDRIVE_SIM_HTML = """
<p>Set the final-drive ratio and toggle cornering to see the differential let the outer wheel spin faster than the inner one.</p>
<div class="sim-panel">
  <div class="viewport"><svg id="fdSvg" viewBox="0 0 300 200" width="100%" height="100%" role="img" aria-label="A final drive reducing speed into torque, feeding a differential and two wheels"></svg></div>
  <div class="sim-row"><span>FINAL DRIVE RATIO</span><span class="mono" id="fdRatioVal">10 : 1</span></div>
  <input id="fdRatioSlider" type="range" min="4" max="40" step="1" value="10">
  <div class="sim-btn-row">
    <button type="button" class="sim-btn active" data-mode="straight">Straight</button>
    <button type="button" class="sim-btn" data-mode="corner">Cornering</button>
  </div>
  <div class="sim-readout" id="fdReadout"></div>
  <p class="sim-note">Input fixed at 1,000 RPM / 200 N·m from the transmission.</p>
</div>"""

FINALDRIVE_SIM_JS = """
<script>
(function(){
  var s=document.getElementById('fdRatioSlider'), val=document.getElementById('fdRatioVal');
  var svg=document.getElementById('fdSvg'), readout=document.getElementById('fdReadout');
  var btns=document.querySelectorAll('.sim-btn[data-mode]');
  if(!s||!svg) return;
  var mode='straight';
  function ns(tag,attrs){ var el=document.createElementNS('http://www.w3.org/2000/svg',tag); for(var k in attrs) el.setAttribute(k,attrs[k]); return el; }
  var style=document.createElement('style');
  style.textContent='@keyframes fdspin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}@media (prefers-reduced-motion:reduce){#fdSvg g{animation:none!important;}}';
  document.head.appendChild(style);
  function draw(){
    var ratio=parseInt(s.value,10); val.textContent=ratio+' : 1';
    var avgRpm=1000/ratio, outTorque=200*ratio;
    var leftRpm= mode==='corner' ? avgRpm*0.85 : avgRpm;
    var rightRpm= mode==='corner' ? avgRpm*1.15 : avgRpm;
    svg.innerHTML='';
    svg.appendChild(ns('circle',{cx:80,cy:60,r:16,fill:'#e8edfb',stroke:'#2454c7','stroke-width':1.5}));
    svg.appendChild(ns('circle',{cx:130,cy:60,r:34,fill:'#f7e8df',stroke:'#c1541d','stroke-width':1.5}));
    svg.appendChild(ns('rect',{x:112,y:100,width:36,height:26,fill:'#5b6672'}));
    svg.appendChild(ns('line',{x1:130,y1:126,x2:70,y2:170,stroke:'#151a1f','stroke-width':4}));
    svg.appendChild(ns('line',{x1:130,y1:126,x2:190,y2:170,stroke:'#151a1f','stroke-width':4}));
    var wl=ns('g',{style:'transform-origin:70px 170px; animation:fdspin '+(60/Math.max(1,leftRpm*0.3)).toFixed(1)+'s linear infinite;'});
    wl.appendChild(ns('circle',{cx:70,cy:170,r:22,fill:'none',stroke:'#151a1f','stroke-width':4}));
    wl.appendChild(ns('line',{x1:70,y1:148,x2:70,y2:192,stroke:'#151a1f','stroke-width':2}));
    svg.appendChild(wl);
    var wr=ns('g',{style:'transform-origin:190px 170px; animation:fdspin '+(60/Math.max(1,rightRpm*0.3)).toFixed(1)+'s linear infinite;'});
    wr.appendChild(ns('circle',{cx:190,cy:170,r:22,fill:'none',stroke:'#151a1f','stroke-width':4}));
    wr.appendChild(ns('line',{x1:190,y1:148,x2:190,y2:192,stroke:'#151a1f','stroke-width':2}));
    svg.appendChild(wr);
    var cells=[['RATIO',ratio+' : 1'],['OUTPUT TORQUE',outTorque+' N·m'],['LEFT WHEEL',leftRpm.toFixed(0)+' RPM'],['RIGHT WHEEL',rightRpm.toFixed(0)+' RPM']];
    readout.innerHTML=cells.map(function(c){return '<div class="cell"><span class="l">'+c[0]+'</span><span class="v">'+c[1]+'</span></div>';}).join('');
  }
  s.addEventListener('input',draw);
  btns.forEach(function(b){ b.addEventListener('click',function(){ btns.forEach(function(x){x.classList.remove('active');}); b.classList.add('active'); mode=b.getAttribute('data-mode'); draw(); }); });
  draw();
})();
</script>"""

BEARING_SIM_HTML = """
<p>A radial ball bearing under load — the balls carry the load through the contact zone as the cage rotates continuously.</p>
<div class="sim-panel">
  <div class="viewport"><svg id="brgSvg" viewBox="0 0 260 260" width="100%" height="100%" role="img" aria-label="A rotating ball bearing cutaway under a radial load"></svg></div>
  <div class="sim-row"><span>RADIAL LOAD</span><span class="mono" id="brgLoadVal">20 kN</span></div>
  <input id="brgLoadSlider" type="range" min="1" max="100" step="1" value="20">
  <div class="sim-readout" id="brgReadout"></div>
  <p class="sim-note">Eight balls share the load; the contact-zone highlight is illustrative, not to stress scale.</p>
</div>"""

BEARING_SIM_JS = """
<script>
(function(){
  var s=document.getElementById('brgLoadSlider'), val=document.getElementById('brgLoadVal');
  var svg=document.getElementById('brgSvg'), readout=document.getElementById('brgReadout');
  if(!s||!svg) return;
  function ns(tag,attrs){ var el=document.createElementNS('http://www.w3.org/2000/svg',tag); for(var k in attrs) el.setAttribute(k,attrs[k]); return el; }
  var cx=130,cy=130,rOut=95,rIn=50,rBall=72;
  var style=document.createElement('style');
  style.textContent='@keyframes brgspin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}@media (prefers-reduced-motion:reduce){#brgCage{animation:none!important;}}';
  document.head.appendChild(style);
  function draw(){
    var load=parseInt(s.value,10); val.textContent=load+' kN';
    var perBall=load/8;
    var level = load<30?'LOW':(load<70?'MODERATE':'HIGH');
    var color = load<30?'#2f7d4f':(load<70?'#c1541d':'#a0261a');
    svg.innerHTML='';
    svg.appendChild(ns('circle',{cx:cx,cy:cy,r:rOut,fill:'none',stroke:'#151a1f','stroke-width':4}));
    svg.appendChild(ns('circle',{cx:cx,cy:cy,r:rIn,fill:'none',stroke:'#151a1f','stroke-width':4}));
    var arcW=10+load*0.4;
    svg.appendChild(ns('path',{d:'M '+(cx-arcW)+' '+(cy-rBall-4)+' A '+(rBall+4)+' '+(rBall+4)+' 0 0 1 '+(cx+arcW)+' '+(cy-rBall-4), fill:'none', stroke:color,'stroke-width':10,'stroke-linecap':'round'}));
    var cage=ns('g',{id:'brgCage',style:'transform-origin:'+cx+'px '+cy+'px; animation:brgspin 6s linear infinite;'});
    for(var i=0;i<8;i++){
      var ang=(i/8)*Math.PI*2, bx=cx+Math.cos(ang)*rBall, by=cy+Math.sin(ang)*rBall;
      cage.appendChild(ns('circle',{cx:bx,cy:by,r:10,fill:'#e8edfb',stroke:'#2454c7','stroke-width':1.5}));
    }
    svg.appendChild(cage);
    var arrow=ns('line',{x1:cx,y1:cy-rOut-30,x2:cx,y2:cy-rOut-6,stroke:color,'stroke-width':Math.max(2,load*0.08)});
    svg.appendChild(arrow);
    svg.appendChild(ns('polygon',{points:(cx-6)+','+(cy-rOut-14)+' '+(cx+6)+','+(cy-rOut-14)+' '+cx+','+(cy-rOut-2), fill:color}));
    var cells=[['RADIAL LOAD',load+' kN'],['LOAD PER BALL',perBall.toFixed(1)+' kN'],['CONTACT LEVEL',level]];
    readout.innerHTML=cells.map(function(c){return '<div class="cell"><span class="l">'+c[0]+'</span><span class="v">'+c[1]+'</span></div>';}).join('');
  }
  s.addEventListener('input',draw);
  draw();
})();
</script>"""

INTERACTIVE_HTML = {
    "gear-ratio": GEAR_SIM_HTML, "hydraulic-force": HYDRAULIC_SIM_HTML,
    "lever-torque": TORQUE_SIM_HTML, "lever-ma": MA_SIM_HTML, "planetary": PLANETARY_SIM_HTML,
    "cylinder-flow": CYLINDER_SIM_HTML, "four-stroke": FOURSTROKE_SIM_HTML,
    "torque-converter": TCONV_SIM_HTML, "final-drive": FINALDRIVE_SIM_HTML, "bearing-cutaway": BEARING_SIM_HTML,
}
INTERACTIVE_JS = {
    "gear-ratio": GEAR_SIM_JS, "hydraulic-force": HYDRAULIC_SIM_JS,
    "lever-torque": TORQUE_SIM_JS, "lever-ma": MA_SIM_JS, "planetary": PLANETARY_SIM_JS,
    "cylinder-flow": CYLINDER_SIM_JS, "four-stroke": FOURSTROKE_SIM_JS,
    "torque-converter": TCONV_SIM_JS, "final-drive": FINALDRIVE_SIM_JS, "bearing-cutaway": BEARING_SIM_JS,
}
INTERACTIVE_TITLE = {
    "gear-ratio": "Gear Pair Simulator", "hydraulic-force": "Hydraulic Force Multiplier",
    "lever-torque": "Lever & Torque", "lever-ma": "Lever Mechanical Advantage", "planetary": "Planetary Gearbox Simulator",
    "cylinder-flow": "Hydraulic Cylinder Stroke", "four-stroke": "Four-Stroke Cycle Animation",
    "torque-converter": "Torque Converter Curve", "final-drive": "Final Drive & Differential", "bearing-cutaway": "Bearing Cutaway",
}


def build_graph():
    return {
        "site": {"title": "Heavy Machinery Encyclopedia", "url": SITE_URL + "/"},
        "categories": CATEGORIES,
        "domains": DOMAINS,
        "machines": [{"slug": m["slug"], "title": m["title"], "category": m["category"], "summary": m["summary"], "principles": [p[0] for p in m["principles"]]} for m in MACHINES],
        "concepts": [{"slug": c["slug"], "title": c["title"], "domain": c["domain"], "definition": c["definition"], "relatedConcepts": c.get("related_concepts", [])} for c in CONCEPTS],
    }


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)


def build_index(graph):
    cat_cards = []
    for cat in CATEGORIES:
        machines = [m for m in MACHINES if m["category"] == cat["id"]]
        if not machines:
            continue
        items = "".join('<li><a href="%smachines/%s/">%s</a></li>' % (BASE, m["slug"], m["title"]) for m in machines)
        cat_cards.append('<div class="cat-card"><h3>%s</h3><ul>%s</ul></div>' % (cat["label"], items))

    domain_cards = []
    for dom in DOMAINS:
        concepts = [c for c in CONCEPTS if c["domain"] == dom["id"]]
        for c in concepts:
            domain_cards.append(
                '<a class="domain-card" href="%sconcepts/%s/"><span class="dc-domain">%s</span><span class="dc-title">%s</span></a>'
                % (BASE, c["slug"], dom["label"], c["title"])
            )

    interactive_cards = []
    for c in CONCEPTS:
        if c.get("interactive"):
            interactive_cards.append(
                '<a class="domain-card" href="%sconcepts/%s/"><span class="dc-domain">%s</span><span class="dc-title">%s</span></a>'
                % (BASE, c["slug"], INTERACTIVE_TITLE[c["interactive"]], c["title"])
            )

    jsonld = json.dumps({"@context": "https://schema.org", "@type": "WebSite", "name": "Heavy Machinery Encyclopedia", "url": SITE_URL + "/"})
    head = HEAD_TMPL.format(
        title="Understand Machines Through Engineering",
        description="An engineering-first encyclopedia of construction, mining, agricultural, and industrial machinery — built around the physics, mathematics, and mechanisms that make each machine work.",
        canonical=SITE_URL + "/", base=BASE, jsonld=jsonld,
    )
    body = []
    body.append('<main>')
    body.append('''
    <section class="idx-hero">
      <span class="chip">20 MACHINES · 10 ENGINEERING CONCEPTS</span>
      <h1>Understand the machine by understanding the engineering underneath it.</h1>
      <p class="lede">Every excavator, crane, and haul truck here is an example, not the subject. The subject is torque, hydraulics, gears, and combustion — the same handful of principles, reused at every scale from a telehandler's boom to the largest crane ever built.</p>
    </section>''')
    body.append('<section class="idx-section" id="quiz-promo"><div class="quiz-promo"><span class="chip">JUST FOR FUN</span><h2>What Kind of Heavy Machine Are You?</h2><p class="idx-dek">A ten-question personality quiz, matched against real specifications from the 20 machines on this site. <a href="%squiz/">Take the quiz →</a></p></div></section>' % BASE)
    body.append('<section class="idx-section" id="machines"><h2>Machines, by Category</h2><p class="idx-dek">Real, named equipment — not generic types — each one cross-linked to the engineering principles that make it work.</p><div class="cat-grid">%s</div></section>' % "".join(cat_cards))
    body.append('<section class="idx-section" id="concepts"><h2>Engineering Fundamentals</h2><p class="idx-dek">The physics and mathematics underneath every machine on this site, with the real machines that apply each one listed automatically on its page.</p><div class="domain-grid">%s</div></section>' % "".join(domain_cards))
    body.append('<section class="idx-section" id="interactive"><h2>Interactive Diagrams</h2><p class="idx-dek">Every engineering concept here includes a live, code-generated diagram — sliders and toggles, not static illustrations.</p><div class="domain-grid">%s</div></section>' % "".join(interactive_cards))
    body.append('</main>')
    foot = FOOT_TMPL.format(base=BASE, pagedata="null")
    write("index.html", head + "\n".join(body) + foot)


def main():
    concepts_by_slug = {c["slug"]: c for c in CONCEPTS}
    graph = build_graph()
    write("data/graph.json", json.dumps(graph, indent=2))

    for m in MACHINES:
        write("machines/%s/index.html" % m["slug"], render_machine(m, concepts_by_slug))
    for c in CONCEPTS:
        write("concepts/%s/index.html" % c["slug"], render_concept(c))

    build_index(graph)

    urls = [SITE_URL + "/", SITE_URL + "/quiz/"] + [SITE_URL + "/machines/%s/" % m["slug"] for m in MACHINES] + [SITE_URL + "/concepts/%s/" % c["slug"] for c in CONCEPTS]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join("  <url><loc>%s</loc></url>\n" % u for u in urls)
    sitemap += "</urlset>\n"
    write("sitemap.xml", sitemap)
    write("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_URL)

    llms = ["# Heavy Machinery Encyclopedia\n", "Machine-readable index: %s/sitemap.xml\n" % SITE_URL,
            "\n## Extras\n", "- [What Kind of Heavy Machine Are You?](%s/quiz/): A ten-question personality quiz matched against real specifications from the 20 machines below.\n" % SITE_URL,
            "\n## Machines\n"]
    for m in MACHINES:
        llms.append("- [%s](%s/machines/%s/): %s\n" % (m["title"], SITE_URL, m["slug"], m["summary"]))
    llms.append("\n## Engineering Concepts\n")
    for c in CONCEPTS:
        llms.append("- [%s](%s/concepts/%s/): %s\n" % (c["title"], SITE_URL, c["slug"], c["definition"]))
    write("llms.txt", "".join(llms))

    print("Built %d machine pages, %d concept pages, index, graph.json, sitemap.xml, robots.txt, llms.txt" % (len(MACHINES), len(CONCEPTS)))


if __name__ == "__main__":
    main()

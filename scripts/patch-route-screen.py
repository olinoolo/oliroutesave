from pathlib import Path
import re
p = Path('android-project/app/src/main/java/com/oli/routesave/ui/compose/RouteSaveComposeApp.kt')
s = p.read_text()
start = s.find('@Composable\nprivate fun RouteScreen(')
end = s.find('@Composable\nprivate fun DriveScreen(', start)
if start < 0 or end < 0: raise SystemExit('RouteScreen boundaries not found')
replacement = r'''@Composable
private fun RouteScreen(onStartNavigation: () -> Unit) {
    val currentLocationLabel = "📍 Aktuálna poloha"
    var origin by rememberSaveable { mutableStateOf("📍 Aktuálna poloha") }
    var destination by rememberSaveable { mutableStateOf("") }
    var loading by rememberSaveable { mutableStateOf(false) }
    var message by rememberSaveable { mutableStateOf("Zadaj štart a cieľ.") }
    var km by rememberSaveable { mutableStateOf<Double?>(null) }
    var minutes by rememberSaveable { mutableStateOf<Double?>(null) }
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val locationPermissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { grants ->
        if (grants[android.Manifest.permission.ACCESS_FINE_LOCATION] == true || grants[android.Manifest.permission.ACCESS_COARSE_LOCATION] == true) {
            message = "Poloha povolená. Stlač ešte raz výpočet trasy."
        } else {
            message = "Prístup k polohe nebol povolený. Zadaj štart ručne."
            origin = ""
        }
    }
    suspend fun geocode(place: String): Pair<Double, Double> = withContext(Dispatchers.IO) {
        val encoded = URLEncoder.encode(place, "UTF-8")
        val c = (URL("https://nominatim.openstreetmap.org/search?q=" + encoded + "&format=json&limit=1").openConnection() as java.net.HttpURLConnection)
        c.connectTimeout = 12000; c.readTimeout = 12000; c.setRequestProperty("User-Agent", "OLI-RouteSave/44.0")
        try { val arr = org.json.JSONArray(c.inputStream.bufferedReader().use { it.readText() }); if (arr.length() == 0) throw IllegalArgumentException("Miesto sa nenašlo: " + place); val item = arr.getJSONObject(0); item.getString("lon").toDouble() to item.getString("lat").toDouble() } finally { c.disconnect() }
    }
    suspend fun route(a: String, b: String): Pair<Double, Double> = withContext(Dispatchers.IO) {
        val from = if (a == currentLocationLabel) {
            val fine = androidx.core.content.ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_FINE_LOCATION) == android.content.pm.PackageManager.PERMISSION_GRANTED
            val coarse = androidx.core.content.ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_COARSE_LOCATION) == android.content.pm.PackageManager.PERMISSION_GRANTED
            if (!fine && !coarse) throw SecurityException("Povoľ prístup k polohe a potom vypočítaj trasu.")
            val manager = context.getSystemService(android.content.Context.LOCATION_SERVICE) as android.location.LocationManager
            val last = try { manager.getLastKnownLocation(android.location.LocationManager.GPS_PROVIDER) } catch (_: Exception) { null }
                ?: try { manager.getLastKnownLocation(android.location.LocationManager.NETWORK_PROVIDER) } catch (_: Exception) { null }
                ?: throw IllegalStateException("Telefón zatiaľ nemá aktuálnu polohu. Zapni GPS alebo zadaj štart ručne.")
            last.longitude to last.latitude
        } else geocode(a)
        val to = geocode(b)
        val url = "https://router.project-osrm.org/route/v1/driving/" + from.first + "," + from.second + ";" + to.first + "," + to.second + "?overview=false"
        val c = (URL(url).openConnection() as java.net.HttpURLConnection); c.connectTimeout = 15000; c.readTimeout = 15000
        try { val json = org.json.JSONObject(c.inputStream.bufferedReader().use { it.readText() }); if (json.optString("code") != "Ok") throw IllegalStateException("Cestnú trasu sa nepodarilo vypočítať."); val r = json.getJSONArray("routes").getJSONObject(0); (r.getDouble("distance") / 1000.0) to (r.getDouble("duration") / 60.0) } finally { c.disconnect() }
    }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
        Text("Plánovanie trasy", fontSize = 25.sp, fontWeight = FontWeight.Bold)
        OutlinedTextField(value = origin, onValueChange = { origin = it; km = null; minutes = null }, label = { Text("Štart (predvolene aktuálna poloha)") }, modifier = Modifier.fillMaxWidth(), singleLine = true)
        OutlinedTextField(value = destination, onValueChange = { destination = it; km = null; minutes = null }, label = { Text("Cieľ") }, modifier = Modifier.fillMaxWidth(), singleLine = true)
        Button(enabled = !loading && origin.isNotBlank() && destination.isNotBlank(), onClick = {
            val fine = androidx.core.content.ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_FINE_LOCATION) == android.content.pm.PackageManager.PERMISSION_GRANTED
            val coarse = androidx.core.content.ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_COARSE_LOCATION) == android.content.pm.PackageManager.PERMISSION_GRANTED
            if (origin == currentLocationLabel && !fine && !coarse) {
                locationPermissionLauncher.launch(arrayOf(android.Manifest.permission.ACCESS_FINE_LOCATION, android.Manifest.permission.ACCESS_COARSE_LOCATION))
                return@Button
            }
            loading = true; message = "Počítam skutočnú cestnú trasu…"
            scope.launch { try { val result = route(origin.trim(), destination.trim()); km = result.first; minutes = result.second; message = "Vzdialenosť vypočítaná podľa cestných údajov."; context.getSharedPreferences("oli_routesave_route", android.content.Context.MODE_PRIVATE).edit().putFloat("last_distance_km", result.first.toFloat()).putString("last_origin", origin.trim()).putString("last_destination", destination.trim()).apply() } catch (e: Exception) { km = null; minutes = null; message = "Trasu sa nepodarilo vypočítať. Skontroluj názvy miest a internet. " + (e.message ?: "") } finally { loading = false } }
        }, modifier = Modifier.fillMaxWidth()) { Text(if (loading) "Počítam…" else "Vypočítať cestnú trasu") }
        MapPlaceholder("Náhľad mapy", Modifier.fillMaxWidth().height(220.dp))
        Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) { Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) { Text("Výsledok trasy", fontWeight = FontWeight.Bold); if (km != null && minutes != null) { Text(String.format(Locale.getDefault(), "%.1f km • približne %.0f min", km, minutes), fontSize = 19.sp, fontWeight = FontWeight.Bold); Text(origin + " → " + destination) } else { Text("Skutočné kilometre sa zobrazia po výpočte.") }; Text(message, color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 12.sp) } }
        Button(onClick = onStartNavigation, modifier = Modifier.fillMaxWidth().height(56.dp), colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.secondary)) { Text("Spustiť navigáciu") }
    }
}

'''
s = s[:start] + replacement + s[end:]
manifest = Path('android-project/app/src/main/AndroidManifest.xml')
if not manifest.exists():
    matches = list(Path('android-project/app/src/main').rglob('AndroidManifest.xml'))
    if not matches: raise SystemExit('AndroidManifest.xml not found')
    manifest = matches[0]
m = manifest.read_text()
permissions = ['android.permission.INTERNET', 'android.permission.ACCESS_COARSE_LOCATION', 'android.permission.ACCESS_FINE_LOCATION']
for permission in permissions:
    if permission not in m:
        m = re.sub(r'(<manifest[^>]*>)', r'\1\n    <uses-permission android:name="' + permission + '" />', m, count=1)
manifest.write_text(m)
p.write_text(s)
print('Route screen now defaults to current location, requests foreground location permission, and calculates road distance using OSRM. If no cached location exists, user can enter a manual start.')
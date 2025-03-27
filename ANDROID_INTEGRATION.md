# Integración con Android

Este documento proporciona ejemplos de código para integrar la API de tareas con una aplicación Android.

## Requisitos previos

Para usar la API desde una aplicación Android, necesitarás:

1. Acceso a Internet en tu aplicación Android (permiso `android.permission.INTERNET`)
2. Biblioteca Retrofit para realizar peticiones HTTP (recomendado)
3. Biblioteca Gson para convertir JSON a objetos Java/Kotlin

## Configuración de dependencias

Añade las siguientes dependencias en tu archivo `build.gradle` (nivel de módulo):

```gradle
dependencies {
    // Retrofit para peticiones HTTP
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    
    // Gson para convertir JSON a objetos
    implementation 'com.google.code.gson:gson:2.10.1'
}
```

## Ejemplo 1: Conexión al endpoint principal de tareas

### 1. Crear modelos de datos (Task.kt)

```kotlin
data class Task(
    val id: Int,
    val title: String,
    val description: String?,
    val priority: String,
    val frequency: String,
    val status: String,
    val start_date: String?,
    val end_date: String?,
    val created_at: String,
    val updated_at: String
)

data class TasksResponse(
    val status: String,
    val count: Int,
    val tasks: List<Task>
)

data class TaskResponse(
    val status: String,
    val task: Task
)
```

### 2. Definir la interfaz de API (ApiService.kt)

```kotlin
interface ApiService {
    @GET("api/tasks")
    suspend fun getTasks(): Response<TasksResponse>
    
    @GET("api/tasks/{id}")
    suspend fun getTask(@Path("id") taskId: Int): Response<TaskResponse>
    
    @GET("api/external/portal/{portalId}")
    suspend fun getExternalPortalTasks(@Path("portalId") portalId: Int): Response<Any>
}
```

### 3. Configurar Retrofit (RetrofitClient.kt)

```kotlin
object RetrofitClient {
    private const val BASE_URL = "https://edc3b852-35d9-4c5a-803d-8b7219b0680a-00-z3b3hb9xg7tr.spock.replit.dev/" // URL específica de tu aplicación Replit
    
    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
    
    val apiService: ApiService by lazy {
        retrofit.create(ApiService::class.java)
    }
}
```

### 4. Ejemplo de uso en un ViewModel

```kotlin
class TasksViewModel : ViewModel() {
    private val _tasks = MutableLiveData<List<Task>>()
    val tasks: LiveData<List<Task>> = _tasks
    
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading
    
    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error
    
    fun loadTasks() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val response = RetrofitClient.apiService.getTasks()
                if (response.isSuccessful) {
                    _tasks.value = response.body()?.tasks ?: emptyList()
                } else {
                    _error.value = "Error: ${response.code()} - ${response.message()}"
                }
            } catch (e: Exception) {
                _error.value = "Error de conexión: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }
}
```

## Ejemplo 2: Conexión al endpoint de portal externo

### 1. Función para cargar tareas del portal externo

```kotlin
fun loadExternalPortalTasks(portalId: Int) {
    viewModelScope.launch {
        _isLoading.value = true
        try {
            val response = RetrofitClient.apiService.getExternalPortalTasks(portalId)
            if (response.isSuccessful) {
                // Como la respuesta puede tener diferentes formatos,
                // debemos manejarla de manera genérica
                val responseBody = response.body()
                if (responseBody is Map<*, *>) {
                    val status = responseBody["status"] as? String
                    val data = responseBody["data"]
                    
                    if (status == "success" && data != null) {
                        // Procesar los datos según la estructura esperada
                        processExternalData(data)
                    } else {
                        _error.value = "Error en la respuesta del portal externo"
                    }
                }
            } else {
                _error.value = "Error: ${response.code()} - ${response.message()}"
            }
        } catch (e: Exception) {
            _error.value = "Error de conexión: ${e.message}"
        } finally {
            _isLoading.value = false
        }
    }
}

private fun processExternalData(data: Any) {
    // Implementar la lógica para procesar los datos del portal externo
    // según la estructura específica esperada
}
```

## Ejemplo completo de Activity

```kotlin
class TasksActivity : AppCompatActivity() {
    private lateinit var binding: ActivityTasksBinding
    private val viewModel: TasksViewModel by viewModels()
    private lateinit var adapter: TasksAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityTasksBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupRecyclerView()
        setupObservers()
        
        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadTasks()
        }
        
        binding.btnLoadExternalTasks.setOnClickListener {
            val portalId = binding.etPortalId.text.toString().toIntOrNull() ?: 1
            viewModel.loadExternalPortalTasks(portalId)
        }
        
        // Cargar tareas al iniciar
        viewModel.loadTasks()
    }
    
    private fun setupRecyclerView() {
        adapter = TasksAdapter()
        binding.recyclerView.adapter = adapter
        binding.recyclerView.layoutManager = LinearLayoutManager(this)
    }
    
    private fun setupObservers() {
        viewModel.tasks.observe(this) { tasks ->
            adapter.submitList(tasks)
        }
        
        viewModel.isLoading.observe(this) { isLoading ->
            binding.swipeRefresh.isRefreshing = isLoading
        }
        
        viewModel.error.observe(this) { errorMsg ->
            if (errorMsg.isNotEmpty()) {
                Toast.makeText(this, errorMsg, Toast.LENGTH_LONG).show()
            }
        }
    }
}
```

## Notas importantes

1. **URL base**: Asegúrate de actualizar la URL base en `RetrofitClient` con la URL real de tu API.

2. **Permisos de Internet**: No olvides añadir el permiso de Internet en tu `AndroidManifest.xml`:
   ```xml
   <uses-permission android:name="android.permission.INTERNET" />
   ```

3. **Manejo de errores**: La implementación anterior proporciona un manejo básico de errores. En producción, deberías implementar una estrategia más robusta.

4. **Hilos secundarios**: Retrofit ya maneja las solicitudes en hilos secundarios, por eso utilizamos `viewModelScope` para evitar bloquear el hilo principal.

5. **Datos del portal externo**: Como la estructura de los datos del portal externo puede variar, la implementación de `processExternalData` debe adaptarse a la estructura específica de los datos.

## Solución de problemas comunes

1. **Error de conexión**:
   - Verifica que la URL base sea correcta
   - Asegúrate de que tu dispositivo tiene conexión a Internet
   - Comprueba si la API está en línea

2. **Errores de deserialiación JSON**:
   - Verifica que los modelos de datos coincidan exactamente con la estructura JSON
   - Considera usar anotaciones Gson como `@SerializedName` para campos con nombres diferentes

3. **Respuestas vacías**:
   - Verifica que la API esté devolviendo datos
   - Comprueba los logs de error en el servidor

4. **Problemas con HTTPS**:
   - Para conexiones HTTPS, es posible que necesites configurar un `TrustManager` personalizado
   - Para desarrollo, puedes permitir tráfico cleartext en tu `AndroidManifest.xml`, pero no se recomienda para producción:
     ```xml
     <application
         android:usesCleartextTraffic="true"
         ...>
     </application>
     ```
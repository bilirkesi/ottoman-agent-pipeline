/**
 * Ottoman Agent - Mobile App (React Native)
 * 
 * Features:
 * - Transliteration
 * - Agent Chat
 * - Workflow Execution
 * - Key Management
 * - History
 */

import React, { useState, useEffect } from 'react';
import {
  AppRegistry,
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  StatusBar,
  SafeAreaView,
  Platform
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Transliterate Screen
function TransliterateScreen() {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [method, setMethod] = useState('');
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('hybrid');

  const handleTransliterate = async () => {
    if (!inputText.trim()) {
      Alert.alert('Error', 'Please enter Ottoman Turkish text');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/transliterate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText, mode })
      });

      const data = await response.json();

      if (data.error) {
        Alert.alert('Error', data.error);
      } else {
        setOutputText(data.modern_turkish || JSON.stringify(data, null, 2));
        setConfidence(data.confidence || 0);
        setMethod(data.method || mode);
      }
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>Ottoman Turkish Transliterator</Text>
        
        <TextInput
          style={styles.input}
          placeholder="عثمانلي توركجهسى..."
          placeholderTextColor="#888"
          value={inputText}
          onChangeText={setInputText}
          multiline
          numberOfLines={4}
          textAlignVertical="top"
        />

        <View style={styles.modeSelector}>
          <Text style={styles.sectionLabel}>Mode:</Text>
          <TouchableOpacity
            style={[styles.modeButton, mode === 'hybrid' && styles.modeButtonActive]}
            onPress={() => setMode('hybrid')}
          >
            <Text style={styles.modeButtonText}>Hybrid</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.modeButton, mode === 'neural' && styles.modeButtonActive]}
            onPress={() => setMode('neural')}
          >
            <Text style={styles.modeButtonText}>Neural</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.modeButton, mode === 'nlp' && styles.modeButtonActive]}
            onPress={() => setMode('nlp')}
          >
            <Text style={styles.modeButtonText}>NLP</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity
          style={[styles.button, styles.primaryButton, loading && styles.buttonDisabled]}
          onPress={handleTransliterate}
          disabled={loading}
        >
          <Text style={styles.buttonText}>{loading ? 'Processing...' : 'Transliterate'}</Text>
        </TouchableOpacity>

        {outputText ? (
          <View style={styles.outputContainer}>
            <Text style={styles.sectionLabel}>Result:</Text>
            <Text style={styles.outputText}>{outputText}</Text>
            <View style={styles.metricsContainer}>
              <Text style={styles.metric}>Confidence: {(confidence * 100).toFixed(1)}%</Text>
              <Text style={styles.metric}>Method: {method}</Text>
            </View>
          </View>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

// Chat Screen
function ChatScreen() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage = { role: 'user', content: inputText, timestamp: Date.now() };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage.content })
      });

      const data = await response.json();

      if (data.error) {
        Alert.alert('Error', data.error);
      } else {
        const assistantMessage = {
          role: 'assistant',
          content: data.output || JSON.stringify(data, null, 2),
          timestamp: Date.now()
        };
        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.chatHeader}>
        <Text style={styles.title}>Agent Chat</Text>
      </View>

      <ScrollView style={styles.messagesContainer}>
        {messages.map((msg, index) => (
          <View
            key={index}
            style={[
              styles.messageBubble,
              msg.role === 'user' ? styles.userMessage : styles.assistantMessage
            ]}
          >
            <Text style={styles.messageText}>{msg.content}</Text>
            <Text style={styles.messageTime}>
              {new Date(msg.timestamp).toLocaleTimeString()}
            </Text>
          </View>
        ))}
        {loading && (
          <View style={styles.messageBubble}>
            <Text style={styles.messageText}>Thinking...</Text>
          </View>
        )}
      </ScrollView>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Type your message..."
          placeholderTextColor="#888"
          value={inputText}
          onChangeText={setInputText}
          multiline
        />
        <TouchableOpacity
          style={[styles.button, styles.primaryButton, !inputText.trim() && styles.buttonDisabled]}
          onPress={sendMessage}
          disabled={!inputText.trim() || loading}
        >
          <Text style={styles.buttonText}>Send</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

// Keys Screen
function KeysScreen() {
  const [keys, setKeys] = useState([]);
  const [service, setService] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [scope, setScope] = useState('global');
  const [loading, setLoading] = useState(false);

  const loadKeys = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/byok/keys`);
      const data = await response.json();
      setKeys(data.keys || []);
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  useEffect(() => {
    loadKeys();
  }, []);

  const createKey = async () => {
    if (!service || !apiKey) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/byok/keys`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ service, api_key: apiKey, scope })
      });

      const data = await response.json();

      if (data.key_id) {
        Alert.alert('Success', `Key created: ${data.key_id}`);
        setService('');
        setApiKey('');
        loadKeys();
      } else {
        Alert.alert('Error', data.detail || 'Failed to create key');
      }
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>API Keys (BYOK)</Text>

        <View style={styles.formContainer}>
          <TextInput
            style={styles.input}
            placeholder="Service (deepseek, gateway, etc.)"
            placeholderTextColor="#888"
            value={service}
            onChangeText={setService}
          />
          <TextInput
            style={styles.input}
            placeholder="API Key"
            placeholderTextColor="#888"
            value={apiKey}
            onChangeText={setApiKey}
            secureTextEntry
          />
          <View style={styles.scopeSelector}>
            <Text style={styles.sectionLabel}>Scope:</Text>
            {['global', 'agent', 'tool', 'user'].map(s => (
              <TouchableOpacity
                key={s}
                style={[styles.scopeButton, scope === s && styles.scopeButtonActive]}
                onPress={() => setScope(s)}
              >
                <Text style={styles.scopeButtonText}>{s}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <TouchableOpacity
            style={[styles.button, styles.primaryButton, loading && styles.buttonDisabled]}
            onPress={createKey}
            disabled={loading}
          >
            <Text style={styles.buttonText}>{loading ? 'Creating...' : 'Create Key'}</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.keysList}>
          <Text style={styles.sectionLabel}>Your Keys:</Text>
          {keys.length === 0 ? (
            <Text style={styles.emptyText}>No keys configured</Text>
          ) : (
            keys.map((key, index) => (
              <View key={index} style={styles.keyItem}>
                <Text style={styles.keyService}>{key.service}</Text>
                <Text style={styles.keyMeta}>
                  {key.key_id} | {key.status}
                </Text>
              </View>
            ))
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// History Screen
function HistoryScreen() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/mcp/tools/history?limit=50`);
      const data = await response.json();
      setHistory(data.calls || []);
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>History</Text>
        
        {loading ? (
          <Text style={styles.loadingText}>Loading...</Text>
        ) : history.length === 0 ? (
          <Text style={styles.emptyText}>No history yet</Text>
        ) : (
          history.map((item, index) => (
            <View key={index} style={styles.historyItem}>
              <Text style={styles.historyTool}>{item.tool_name}</Text>
              <Text style={styles.historyMeta}>
                {new Date(item.started_at).toLocaleString()} | {item.duration_ms.toFixed(0)}ms
                {item.error ? ' ❌' : ' ✅'}
              </Text>
            </View>
          ))
        )}

        <TouchableOpacity style={styles.button} onPress={loadHistory}>
          <Text style={styles.buttonText}>Refresh</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

// Main App
const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;

            if (route.name === 'Transliterate') {
              iconName = focused ? 'text' : 'text-outline';
            } else if (route.name === 'Chat') {
              iconName = focused ? 'chatbubbles' : 'chatbubbles-outline';
            } else if (route.name === 'Keys') {
              iconName = focused ? 'key' : 'key-outline';
            } else if (route.name === 'History') {
              iconName = focused ? 'time' : 'time-outline';
            }

            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#e94560',
          tabBarInactiveTintColor: 'gray',
          headerStyle: {
            backgroundColor: '#1a1a2e',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        })}
      >
        <Tab.Screen name="Transliterate" component={TransliterateScreen} />
        <Tab.Screen name="Chat" component={ChatScreen} />
        <Tab.Screen name="Keys" component={KeysScreen} />
        <Tab.Screen name="History" component={HistoryScreen} />
      </Tab.Navigator>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  scrollContent: {
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
    textAlign: 'center',
  },
  sectionLabel: {
    fontSize: 14,
    color: '#a0a0a0',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#16213e',
    borderColor: '#2a2a4a',
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    color: '#fff',
    fontSize: 16,
    marginBottom: 12,
    minHeight: 100,
  },
  modeSelector: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 12,
  },
  modeButton: {
    padding: 10 20,
    backgroundColor: '#16213e',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#2a2a4a',
  },
  modeButtonActive: {
    backgroundColor: '#e94560',
    borderColor: '#e94560',
  },
  modeButtonText: {
    color: '#fff',
    fontWeight: '500',
  },
  button: {
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  primaryButton: {
    backgroundColor: '#e94560',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  outputContainer: {
    marginTop: 16,
    padding: 16,
    backgroundColor: '#16213e',
    borderRadius: 8,
  },
  outputText: {
    color: '#fff',
    fontSize: 16,
    fontFamily: 'Courier New',
    marginBottom: 8,
  },
  metricsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  metric: {
    color: '#a0a0a0',
    fontSize: 14,
  },
  chatHeader: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a4a',
  },
  messagesContainer: {
    flex: 1,
    padding: 16,
  },
  messageBubble: {
    padding: 12,
    borderRadius: 12,
    marginBottom: 8,
    maxWidth: '80%',
  },
  userMessage: {
    backgroundColor: '#0f3460',
    alignSelf: 'flex-end',
  },
  assistantMessage: {
    backgroundColor: '#533483',
    alignSelf: 'flex-start',
  },
  messageText: {
    color: '#fff',
    fontSize: 16,
  },
  messageTime: {
    color: '#888',
    fontSize: 12,
    marginTop: 4,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#2a2a4a',
  },
  formContainer: {
    marginBottom: 16,
  },
  scopeSelector: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 12,
  },
  scopeButton: {
    padding: 8 16,
    backgroundColor: '#16213e',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#2a2a4a',
  },
  scopeButtonActive: {
    backgroundColor: '#e94560',
    borderColor: '#e94560',
  },
  scopeButtonText: {
    color: '#fff',
    fontSize: 14,
  },
  keysList: {
    marginTop: 16,
  },
  keyItem: {
    backgroundColor: '#16213e',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  keyService: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  keyMeta: {
    color: '#888',
    fontSize: 12,
    marginTop: 4,
  },
  historyItem: {
    backgroundColor: '#16213e',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  historyTool: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  historyMeta: {
    color: '#888',
    fontSize: 12,
    marginTop: 4,
  },
  loadingText: {
    color: '#888',
    textAlign: 'center',
    marginTop: 20,
  },
  emptyText: {
    color: '#888',
    textAlign: 'center',
    marginTop: 20,
  },
});

// Register app
AppRegistry.registerComponent('OttomanAgent', () => App);

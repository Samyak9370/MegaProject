import React, { useState, useRef, useEffect, memo } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  CircularProgress,
  Chip,
  Grid,
  LinearProgress,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Collapse,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Mic as MicIcon,
  Stop as StopIcon,
  VolumeUp as VolumeUpIcon,
  SentimentSatisfied as SentimentSatisfiedIcon,
  Speed as SpeedIcon,
  Gavel as GavelIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Error as ErrorIcon,
  History as HistoryIcon,
} from '@mui/icons-material';

// MetricCard component
const MetricCard = memo(({ title, value, icon: Icon, color = 'primary', max = 10 }) => {
  const isPercentage = typeof value === 'number' && value <= 1;
  const displayValue = isPercentage ? `${Math.round(value * 100)}%` : (typeof value === 'number' ? value.toFixed(1) : value);

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={1}>
          <Icon color={color} sx={{ mr: 1 }} />
          <Typography variant="h6" component="div">
            {title}
          </Typography>
        </Box>
        <Box display="flex" alignItems="center">
          <Typography variant="h4" component="div" sx={{ flexGrow: 1 }}>
            {displayValue}
          </Typography>
          {typeof value === 'number' && max && (
            <Box width="60%" ml={2}>
              <LinearProgress
                variant="determinate"
                value={isPercentage ? value * 100 : (value / max) * 100}
                color={color}
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
});

// FeedbackItem component
const FeedbackItem = memo(({ type, text }) => {
  const [expanded, setExpanded] = useState(false);

  const getIcon = () => {
    switch (type) {
      case 'strength':
        return <CheckCircleIcon color="success" />;
      case 'improvement':
        return <WarningIcon color="warning" />;
      case 'suggestion':
      case 'ai_reply':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon color="primary" />;
    }
  };

  return (
    <>
      <ListItem
        button
        onClick={() => setExpanded(!expanded)}
        sx={{
          borderLeft: `4px solid ${
            type === 'strength' ? '#4caf50' : type === 'improvement' ? '#ff9800' : '#2196f3'
          }`,
          mb: 1,
          borderRadius: 1,
        }}
      >
        <ListItemIcon>{getIcon()}</ListItemIcon>
        <ListItemText
          primary={text}
          primaryTypographyProps={{
            variant: 'body2',
            style: { whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' },
          }}
        />
        {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
      </ListItem>
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <Box px={4} py={2}>
          <Typography variant="body2" color="text.secondary">
            {text}
          </Typography>
        </Box>
      </Collapse>
    </>
  );
});

// TabPanel component
function TabPanel(props) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} id={`tabpanel-${index}`} aria-labelledby={`tab-${index}`} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const DebateAnalyzer = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId] = useState(`session-${Date.now()}`);
  const [transcript, setTranscript] = useState('');
  const [aiReply, setAiReply] = useState('');
  const [analysis, setAnalysis] = useState({
    metrics: {
      word_count: 0,
      unique_words: 0,
      vocabulary_richness: 0,
      avg_word_length: 0,
      sentence_count: 0,
      filler_word_count: 0,
      grammar_errors: 0,
      hesitation_count: 0,
      speaking_rate: 0,
      overall_score: 0,
      clarity_score: 0,
      confidence_score: 0,
      fluency_score: 0,
    },
    feedback: {
      strengths: [],
      areas_for_improvement: [],
      suggestions: [],
    },
    session_summary: null,
  });
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [history, setHistory] = useState([]);
  const [tabValue, setTabValue] = useState(0);

  const mediaRecorderRef = useRef(null);
  const wsRef = useRef(null);
  const sessionStartTimeRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Log MIME type support
  useEffect(() => {
    console.log('MediaRecorder support:', {
      webmOpus: MediaRecorder.isTypeSupported('audio/webm;codecs=opus'),
      webm: MediaRecorder.isTypeSupported('audio/webm'),
      oggOpus: MediaRecorder.isTypeSupported('audio/ogg;codecs=opus'),
    });
  }, []);

  // Fetch session history
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`http://localhost:8000/history/${sessionId}`);
        const data = await response.json();
        setHistory(data);
      } catch (err) {
        setError({ severity: 'error', message: 'Failed to fetch session history' });
      }
    };
    fetchHistory();
  }, [sessionId]);

  // WebSocket connection
  useEffect(() => {
    if (!isRecording) return;

    const connectWebSocket = () => {
      const wsUrl = `ws://localhost:8000/ws/debate/${sessionId}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setError(null);
        ws.send(JSON.stringify({ type: 'connection_init' }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          switch (data.type) {
            case 'analysis_update':
              setAnalysis((prev) => ({
                ...prev,
                metrics: { ...prev.metrics, ...data.metrics },
                feedback: { ...prev.feedback, ...data.feedback },
              }));
              setTranscript(data.full_transcript || data.transcript || '');
              setAiReply(data.ai_reply || '');
              setIsAnalyzing(false);
              break;
            case 'session_summary':
              setAnalysis((prev) => ({ ...prev, session_summary: data }));
              setHistory((prev) => [...prev, data]);
              setIsAnalyzing(false);
              break;
            case 'error':
              setError({ severity: 'error', message: data.message });
              setIsAnalyzing(false);
              break;
            case 'warning':
              setError({ severity: 'warning', message: data.message });
              setIsAnalyzing(false);
              break;
            case 'connection_ack':
              console.log('Connection acknowledged');
              break;
            case 'pong':
              break;
            default:
              console.warn('Unhandled message type:', data.type);
          }
        } catch (err) {
          setError({ severity: 'error', message: 'Error processing server response' });
        }
      };

      ws.onerror = () => {
        setError({ severity: 'warning', message: 'Connection error' });
      };

      ws.onclose = () => {
        if (isRecording) {
          setTimeout(connectWebSocket, 2000);
        }
      };

      wsRef.current = ws;
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [isRecording, sessionId]);

  // Volume visualization
  useEffect(() => {
    if (!isRecording || !analyserRef.current) return;

    const updateVolume = () => {
      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
      analyserRef.current.getByteFrequencyData(dataArray);
      const avg = dataArray.reduce((a, b) => a + b) / dataArray.length;
      setVolumeLevel(Math.min(100, Math.round((avg / 255) * 100)));
      if (isRecording) {
        animationFrameRef.current = requestAnimationFrame(updateVolume);
      }
    };

    updateVolume();

    return () => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, [isRecording]);

  // Start recording
  const startRecording = async () => {
    try {
      setError(null);
      setTranscript('');
      setAiReply('');
      setAnalysis({
        metrics: {
          word_count: 0,
          unique_words: 0,
          vocabulary_richness: 0,
          avg_word_length: 0,
          sentence_count: 0,
          filler_word_count: 0,
          grammar_errors: 0,
          hesitation_count: 0,
          speaking_rate: 0,
          overall_score: 0,
          clarity_score: 0,
          confidence_score: 0,
          fluency_score: 0,
        },
        feedback: {
          strengths: [],
          areas_for_improvement: [],
          suggestions: [],
        },
        session_summary: null,
      });
      audioChunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          sampleSize: 16,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 16000,
      });
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      source.connect(analyserRef.current);

      const mimeTypes = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus'];
      let selectedMimeType = null;
      for (const mimeType of mimeTypes) {
        if (MediaRecorder.isTypeSupported(mimeType)) {
          selectedMimeType = mimeType;
          break;
        }
      }
      if (!selectedMimeType) {
        throw new Error('No supported audio MIME types available');
      }
      console.log('Selected MIME type:', selectedMimeType);

      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: selectedMimeType,
        audioBitsPerSecond: 16000,
      });

      mediaRecorderRef.current.ondataavailable = async (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          console.log('Audio chunk size:', event.data.size);
          if (audioChunksRef.current.length >= 15 && wsRef.current?.readyState === WebSocket.OPEN) { // Wait for 5 chunks (5 seconds)
            setIsAnalyzing(true);
            try {
              const audioBlob = new Blob(audioChunksRef.current, { type: selectedMimeType });
              if (audioBlob.size < 1000) {
                console.warn('Audio blob too small:', audioBlob.size);
                setIsAnalyzing(false);
                return;
              }
              const arrayBuffer = await audioBlob.arrayBuffer();
              const base64String = btoa(
                new Uint8Array(arrayBuffer).reduce((data, byte) => data + String.fromCharCode(byte), '')
              );
              audioChunksRef.current = [];
              const duration = 15; // Approximate duration of 5 chunks

              wsRef.current.send(
                JSON.stringify({
                  type: 'audio_chunk',
                  data: base64String,
                  duration_seconds: duration,
                  mime_type: selectedMimeType,
                })
              );
            } catch (err) {
              setError({ severity: 'error', message: `Error processing audio: ${err.message}` });
              setIsAnalyzing(false);
            }
          }
        }
      };

      mediaRecorderRef.current.start(1000); // Collect chunks every 1 second
      setIsRecording(true);
      sessionStartTimeRef.current = Date.now();
    } catch (err) {
      setError({ severity: 'error', message: `Could not access microphone: ${err.message}` });
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: 'session_end',
            session_duration_seconds: (Date.now() - sessionStartTimeRef.current) / 1000,
          })
        );
      }
      setIsRecording(false);
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close();
    }
  };

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Error UI
  if (error) {
    return (
      <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
        <Paper elevation={3} sx={{ p: 3, textAlign: 'center' }}>
          <ErrorIcon color="error" sx={{ fontSize: 60, mb: 2 }} />
          <Typography variant="h5" color="error" gutterBottom>
            An error occurred
          </Typography>
          <Typography paragraph>{error.message}</Typography>
          <Button variant="contained" color="primary" onClick={() => setError(null)} sx={{ mt: 2 }}>
            Try Again
          </Button>
        </Paper>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h3" gutterBottom textAlign="center">
        AI Debate Analyzer
      </Typography>

      <Tabs value={tabValue} onChange={handleTabChange} centered sx={{ mb: 3 }}>
        <Tab label="Live Analysis" icon={<MicIcon />} />
        <Tab label="Session History" icon={<HistoryIcon />} />
      </Tabs>

      <TabPanel value={tabValue} index={0}>
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h4" component="h1">
              Live Analysis
            </Typography>
            <Box>
              {!isRecording ? (
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<MicIcon />}
                  onClick={startRecording}
                  disabled={isAnalyzing}
                  size="large"
                >
                  Start Recording
                </Button>
              ) : (
                <Button
                  variant="contained"
                  color="secondary"
                  startIcon={<StopIcon />}
                  onClick={stopRecording}
                  size="large"
                >
                  Stop Recording
                </Button>
              )}
            </Box>
          </Box>

          {error && (
            <Box sx={{ mb: 2, p: 2, bgcolor: error.severity === 'error' ? 'error.light' : 'warning.light', borderRadius: 1 }}>
              {error.severity === 'error' ? <ErrorIcon color="error" sx={{ mr: 1 }} /> : <WarningIcon color="warning" sx={{ mr: 1 }} />}
              <Typography color={error.severity}>{error.message}</Typography>
            </Box>
          )}

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" mb={1}>Live Transcript</Typography>
            <Paper variant="outlined" sx={{ p: 2, minHeight: 150, maxHeight: 300, overflowY: 'auto', bgcolor: 'background.paper' }}>
              {transcript || (
                <Typography color="textSecondary" fontStyle="italic">
                  {isRecording ? 'Start speaking...' : 'Press Start Recording to begin'}
                </Typography>
              )}
            </Paper>
          </Box>

          {aiReply && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" mb={1}>AI Feedback</Typography>
              <Paper variant="outlined" sx={{ p: 2, bgcolor: 'info.light' }}>
                <Typography variant="body1">{aiReply}</Typography>
              </Paper>
            </Box>
          )}

          {isRecording && (
            <Box sx={{ mb: 3 }}>
              <Box display="flex" alignItems="center" mb={1}>
                <VolumeUpIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="subtitle2">Volume Level</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box sx={{ width: '100%', mr: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={volumeLevel}
                    sx={{
                      height: 10,
                      borderRadius: 5,
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: volumeLevel > 80 ? '#f44336' : volumeLevel > 50 ? '#ff9800' : '#4caf50',
                      },
                    }}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ minWidth: 40, textAlign: 'right' }}>
                  {volumeLevel}%
                </Typography>
              </Box>
            </Box>
          )}

          {(isAnalyzing || analysis.metrics.overall_score > 0) && (
            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
              <Typography variant="h5" gutterBottom>Analysis</Typography>
              {isAnalyzing ? (
                <Box display="flex" justifyContent="center" alignItems="center" p={4}>
                  <CircularProgress />
                  <Typography variant="body1" sx={{ ml: 2 }}>Analyzing your speech...</Typography>
                </Box>
              ) : (
                <Box>
                  <Grid container spacing={3} sx={{ mb: 3 }}>
                    <Grid item xs={12} md={3}>
                      <MetricCard title="Overall Score" value={analysis.metrics.overall_score} icon={SentimentSatisfiedIcon} max={10} />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <MetricCard title="Speaking Rate" value={`${Math.round(analysis.metrics.speaking_rate)} wpm`} icon={SpeedIcon} color="secondary" />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <MetricCard title="Clarity Score" value={analysis.metrics.clarity_score} icon={VolumeUpIcon} color="success" max={10} />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <MetricCard title="Confidence Score" value={analysis.metrics.confidence_score} icon={GavelIcon} color="info" max={10} />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <MetricCard title="Fluency Score" value={analysis.metrics.fluency_score} icon={SpeedIcon} color="warning" max={10} />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <MetricCard title="Vocabulary Richness" value={analysis.metrics.vocabulary_richness} icon={GavelIcon} color="success" max={1} />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <MetricCard title="Grammar Errors" value={analysis.metrics.grammar_errors} icon={WarningIcon} color="error" />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <MetricCard title="Filler Words" value={analysis.metrics.filler_word_count} icon={WarningIcon} color="error" />
                    </Grid>
                  </Grid>

                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 2, height: '100%' }}>
                        <Typography variant="h6" gutterBottom>Strengths</Typography>
                        {analysis.feedback.strengths.length > 0 ? (
                          <List dense>
                            {analysis.feedback.strengths.map((strength, index) => (
                              <FeedbackItem key={index} type="strength" text={strength} />
                            ))}
                          </List>
                        ) : (
                          <Typography color="textSecondary" fontStyle="italic">
                            No strengths identified yet.
                          </Typography>
                        )}
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 2, height: '100%' }}>
                        <Typography variant="h6" gutterBottom>Areas for Improvement</Typography>
                        {analysis.feedback.areas_for_improvement.length > 0 ? (
                          <List dense>
                            {analysis.feedback.areas_for_improvement.map((item, index) => (
                              <FeedbackItem key={index} type="improvement" text={item} />
                            ))}
                          </List>
                        ) : (
                          <Typography color="textSecondary" fontStyle="italic">
                            No areas for improvement identified yet.
                          </Typography>
                        )}
                      </Paper>
                    </Grid>
                  </Grid>

                  {analysis.feedback.suggestions.length > 0 && (
                    <Box mt={3}>
                      <Typography variant="h6" gutterBottom>Suggestions</Typography>
                      <List>
                        {analysis.feedback.suggestions.map((suggestion, index) => (
                          <FeedbackItem key={index} type={index === analysis.feedback.suggestions.length - 1 ? 'ai_reply' : 'suggestion'} text={suggestion} />
                        ))}
                      </List>
                    </Box>
                  )}
                </Box>
              )}
            </Paper>
          )}

          {analysis.session_summary && (
            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h5">Session Summary</Typography>
                <Chip label="Completed" color="success" variant="outlined" icon={<CheckCircleIcon />} />
              </Box>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Session Duration: {Math.round(analysis.session_summary.duration_minutes * 10) / 10} minutes
                  </Typography>
                  <Typography variant="subtitle1" gutterBottom>
                    Total Words: {analysis.session_summary.total_words}
                  </Typography>
                  <Typography variant="subtitle1" gutterBottom>
                    Average Speaking Rate: {Math.round(analysis.session_summary.avg_words_per_minute)} wpm
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Filler Words: {analysis.session_summary.filler_word_rate.toFixed(1)}% of words
                  </Typography>
                  <Typography variant="subtitle1" gutterBottom>
                    Vocabulary Richness: {(analysis.session_summary.vocabulary_richness * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="subtitle1" gutterBottom>
                    Overall Score: {analysis.session_summary.overall_score.toFixed(1)}/10
                  </Typography>
                </Grid>
              </Grid>
              {analysis.session_summary.key_takeaways.length > 0 && (
                <Box mt={3}>
                  <Typography variant="h6" gutterBottom>Key Takeaways</Typography>
                  <List>
                    {analysis.session_summary.key_takeaways.map((takeaway, index) => (
                      <FeedbackItem key={index} type="suggestion" text={takeaway} />
                    ))}
                  </List>
                </Box>
              )}
              <Box mt={3} textAlign="center">
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<MicIcon />}
                  onClick={startRecording}
                  size="large"
                >
                  Start New Session
                </Button>
              </Box>
            </Paper>
          )}
          </Paper>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>Session History</Typography>
            {history.length > 0 ? (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Duration (min)</TableCell>
                    <TableCell>Total Words</TableCell>
                    <TableCell>Speaking Rate (wpm)</TableCell>
                    <TableCell>Overall Score</TableCell>
                    <TableCell>Clarity Score</TableCell>
                    <TableCell>Confidence Score</TableCell>
                    <TableCell>Fluency Score</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {history.map((session, index) => (
                    <TableRow key={index}>
                      <TableCell>{new Date(session.timestamp).toLocaleString()}</TableCell>
                      <TableCell>{Math.round(session.duration_minutes * 10) / 10}</TableCell>
                      <TableCell>{session.total_words}</TableCell>
                      <TableCell>{Math.round(session.avg_words_per_minute)}</TableCell>
                      <TableCell>{session.overall_score.toFixed(1)}</TableCell>
                      <TableCell>{session.clarity_score.toFixed(1)}</TableCell>
                      <TableCell>{session.confidence_score.toFixed(1)}</TableCell>
                      <TableCell>{session.fluency_score.toFixed(1)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <Typography color="textSecondary" fontStyle="italic">
                No session history available.
              </Typography>
            )}
          </Paper>
        </TabPanel>
    </Box>
  );
};

export default DebateAnalyzer;

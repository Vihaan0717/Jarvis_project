import { EmotionType, PoseType } from '@/animation/types';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import {
  Smile, Frown, Angry, Heart, Meh, Sparkles, Brain, Shield,
  Camera, CameraOff, Upload,
  PersonStanding, Footprints, Armchair, Music, Hand, ArrowDown,
  Zap, MoveUp, ThermometerSnowflake, Snowflake,
  Eye, Droplets, CircleDot, Trophy, AlertCircle,
} from 'lucide-react';

interface ControlPanelProps {
  emotion: EmotionType;
  pose: PoseType;
  tracking: boolean;
  exertion: number;
  onEmotionChange: (e: EmotionType) => void;
  onPoseChange: (p: PoseType) => void;
  onToggleTracking: () => void;
  onUploadModel: () => void;
  onExertionChange: (v: number) => void;
  hasModel: boolean;
}

const emotions: { id: EmotionType; label: string; icon: React.ReactNode }[] = [
  { id: 'neutral', label: 'Neutral', icon: <Meh className="w-4 h-4" /> },
  { id: 'happy', label: 'Happy', icon: <Smile className="w-4 h-4" /> },
  { id: 'sad_mild', label: 'Sad', icon: <Frown className="w-4 h-4" /> },
  { id: 'sad_moderate', label: 'Sad++', icon: <Frown className="w-4 h-4" /> },
  { id: 'sad_severe', label: 'Cry', icon: <Droplets className="w-4 h-4" /> },
  { id: 'angry', label: 'Angry', icon: <Angry className="w-4 h-4" /> },
  { id: 'surprised', label: 'Surprised', icon: <Sparkles className="w-4 h-4" /> },
  { id: 'relaxed', label: 'Love', icon: <Heart className="w-4 h-4" /> },
  { id: 'thinking', label: 'Thinking', icon: <Brain className="w-4 h-4" /> },
  { id: 'serious', label: 'Serious', icon: <Shield className="w-4 h-4" /> },
  { id: 'fever', label: 'Fever', icon: <ThermometerSnowflake className="w-4 h-4" /> },
  { id: 'cold', label: 'Cold', icon: <Snowflake className="w-4 h-4" /> },
];

const poses: { id: PoseType; label: string; icon: React.ReactNode; group?: string }[] = [
  // Core
  { id: 'idle', label: 'Idle', icon: <PersonStanding className="w-4 h-4" />, group: 'core' },
  { id: 'walk', label: 'Walk', icon: <Footprints className="w-4 h-4" />, group: 'core' },
  { id: 'run', label: 'Run', icon: <Zap className="w-4 h-4" />, group: 'core' },
  { id: 'jump', label: 'Jump', icon: <MoveUp className="w-4 h-4" />, group: 'core' },
  // Sitting
  { id: 'sit', label: 'Sit', icon: <Armchair className="w-4 h-4" />, group: 'sit' },
  { id: 'seiza', label: 'Seiza', icon: <ArrowDown className="w-4 h-4" />, group: 'sit' },
  { id: 'agura', label: 'Agura', icon: <Armchair className="w-4 h-4" />, group: 'sit' },
  // Gestures
  { id: 'wave', label: 'Wave', icon: <Hand className="w-4 h-4" />, group: 'gesture' },
  { id: 'bow', label: 'Bow', icon: <ArrowDown className="w-4 h-4" />, group: 'gesture' },
  { id: 'dance', label: 'Dance', icon: <Music className="w-4 h-4" />, group: 'gesture' },
  // Expressive
  { id: 'think', label: 'Think', icon: <Brain className="w-4 h-4" />, group: 'expressive' },
  { id: 'cry', label: 'Cry', icon: <Droplets className="w-4 h-4" />, group: 'expressive' },
  { id: 'shiver', label: 'Shiver', icon: <ThermometerSnowflake className="w-4 h-4" />, group: 'expressive' },
  { id: 'hug_self', label: 'Hug Self', icon: <Snowflake className="w-4 h-4" />, group: 'expressive' },
  // Easter eggs
  { id: 'gasp', label: 'Gasp!', icon: <AlertCircle className="w-4 h-4" />, group: 'fun' },
  { id: 'peace_sign', label: 'Peace ✌️', icon: <Trophy className="w-4 h-4" />, group: 'fun' },
  { id: 'peekaboo', label: 'Peek-a-boo!', icon: <Eye className="w-4 h-4" />, group: 'fun' },
  // Counting
  { id: 'count_1', label: '1 ☝️', icon: <Hand className="w-4 h-4" />, group: 'counting' },
  { id: 'count_2', label: '2 ✌️', icon: <Hand className="w-4 h-4" />, group: 'counting' },
  { id: 'count_3', label: '3 🤟', icon: <Hand className="w-4 h-4" />, group: 'counting' },
  { id: 'count_4', label: '4 🖖', icon: <Hand className="w-4 h-4" />, group: 'counting' },
  { id: 'count_5', label: '5 🖐', icon: <Hand className="w-4 h-4" />, group: 'counting' },
];

export default function ControlPanel({
  emotion, pose, tracking, exertion,
  onEmotionChange, onPoseChange, onToggleTracking, onUploadModel, onExertionChange, hasModel,
}: ControlPanelProps) {
  return (
    <div className="absolute right-4 top-4 bottom-4 w-64 flex flex-col gap-3 z-10 overflow-y-auto">
      {!hasModel && (
        <Card className="p-4 bg-card/80 backdrop-blur-xl border-border">
          <Button onClick={onUploadModel} className="w-full gap-2" variant="default">
            <Upload className="w-4 h-4" /> Load VRM Model
          </Button>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            Upload a .vrm file to get started
          </p>
        </Card>
      )}

      <Card className="p-4 bg-card/80 backdrop-blur-xl border-border">
        <h3 className="text-sm font-semibold text-foreground mb-3">Face Tracking</h3>
        <Button
          onClick={onToggleTracking}
          variant={tracking ? 'destructive' : 'default'}
          className="w-full gap-2"
          disabled={!hasModel}
        >
          {tracking ? <CameraOff className="w-4 h-4" /> : <Camera className="w-4 h-4" />}
          {tracking ? 'Stop Tracking' : 'Start Tracking'}
        </Button>
      </Card>

      <Card className="p-4 bg-card/80 backdrop-blur-xl border-border">
        <h3 className="text-sm font-semibold text-foreground mb-3">Expressions</h3>
        <div className="grid grid-cols-2 gap-2">
          {emotions.map(e => (
            <Button
              key={e.id}
              variant={emotion === e.id ? 'default' : 'outline'}
              size="sm"
              className="gap-1.5 text-xs"
              onClick={() => onEmotionChange(e.id)}
              disabled={!hasModel}
            >
              {e.icon} {e.label}
            </Button>
          ))}
        </div>
      </Card>

      <Card className="p-4 bg-card/80 backdrop-blur-xl border-border">
        <h3 className="text-sm font-semibold text-foreground mb-3">Poses</h3>
        <div className="space-y-3">
          {(['core', 'sit', 'gesture', 'expressive', 'fun', 'counting'] as const).map(group => {
            const groupPoses = poses.filter(p => p.group === group);
            const labels: Record<string, string> = {
              core: 'Locomotion',
              sit: 'Sitting',
              gesture: 'Gestures',
              expressive: 'Emotional',
              fun: 'Easter Eggs',
              counting: 'Counting',
            };
            return (
              <div key={group}>
                <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1.5 font-medium">
                  {labels[group]}
                </p>
                <div className="grid grid-cols-2 gap-1.5">
                  {groupPoses.map(p => (
                    <Button
                      key={p.id}
                      variant={pose === p.id ? 'default' : 'outline'}
                      size="sm"
                      className="gap-1.5 text-xs"
                      onClick={() => onPoseChange(p.id)}
                      disabled={!hasModel}
                    >
                      {p.icon} {p.label}
                    </Button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      <Card className="p-4 bg-card/80 backdrop-blur-xl border-border">
        <h3 className="text-sm font-semibold text-foreground mb-3">Exertion Level</h3>
        <Slider
          value={[exertion * 100]}
          onValueChange={([v]) => onExertionChange(v / 100)}
          max={100}
          step={1}
          disabled={!hasModel}
        />
        <p className="text-xs text-muted-foreground mt-1 text-center">
          {Math.round(exertion * 100)}% — affects breathing intensity
        </p>
      </Card>

      {hasModel && (
        <Card className="p-4 bg-card/80 backdrop-blur-xl border-border">
          <Button onClick={onUploadModel} variant="outline" className="w-full gap-2" size="sm">
            <Upload className="w-4 h-4" /> Change Model
          </Button>
        </Card>
      )}
    </div>
  );
}

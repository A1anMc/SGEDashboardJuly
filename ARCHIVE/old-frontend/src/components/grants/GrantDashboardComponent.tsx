import React from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Typography from '@mui/material/Typography';
import LinearProgress from '@mui/material/LinearProgress';
import Chip from '@mui/material/Chip';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';

interface DashboardData {
  metrics: {
    total_active: number;
    total_value: number;
    success_rate: number;
    pending_applications: number;
  };
  status_distribution: {
    name: string;
    value: number;
  }[];
  monthly_applications: {
    month: string;
    applications: number;
  }[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

interface GrantDashboardProps {
  dashboard: DashboardData;
}

export default function GrantDashboardComponent({ dashboard }: GrantDashboardProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" sx={{ mb: 4 }}>Grants Dashboard</Typography>

      {/* Metrics Overview */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 3, mb: 4 }}>
        <Card sx={{ p: 2, height: '100%' }}>
          <Typography variant="h6" color="primary">Active Grants</Typography>
          <Typography variant="h3">{dashboard.metrics.total_active}</Typography>
        </Card>
        <Card sx={{ p: 2, height: '100%' }}>
          <Typography variant="h6" color="primary">Total Value</Typography>
          <Typography variant="h3">{formatCurrency(dashboard.metrics.total_value)}</Typography>
        </Card>
        <Card sx={{ p: 2, height: '100%' }}>
          <Typography variant="h6" color="primary">Success Rate</Typography>
          <Typography variant="h3">{dashboard.metrics.success_rate}%</Typography>
          <LinearProgress 
            variant="determinate" 
            value={dashboard.metrics.success_rate} 
            sx={{ mt: 1 }}
          />
        </Card>
        <Card sx={{ p: 2, height: '100%' }}>
          <Typography variant="h6" color="primary">Pending Applications</Typography>
          <Typography variant="h3">{dashboard.metrics.pending_applications}</Typography>
        </Card>
      </Box>

      {/* Charts */}
      <Box sx={{ display: 'grid', gridTemplateColumns: '8fr 4fr', gap: 3 }}>
        <Card sx={{ p: 2, height: '100%' }}>
          <Typography variant="h6" sx={{ mb: 2 }}>Monthly Applications</Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dashboard.monthly_applications}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="applications" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card sx={{ p: 2, height: '100%' }}>
          <Typography variant="h6" sx={{ mb: 2 }}>Status Distribution</Typography>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={dashboard.status_distribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {dashboard.status_distribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {dashboard.status_distribution.map((entry, index) => (
              <Chip
                key={entry.name}
                label={`${entry.name}: ${entry.value}`}
                sx={{
                  backgroundColor: COLORS[index % COLORS.length],
                  color: 'white',
                }}
              />
            ))}
          </Box>
        </Card>
      </Box>
    </Box>
  );
} 
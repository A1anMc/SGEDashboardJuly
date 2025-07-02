import React from 'react';
import { Card, Grid, Typography, Box, Chip, LinearProgress } from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { fetchGrantDashboard } from '@/services/grants';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const GrantDashboard: React.FC = () => {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['grantDashboard'],
    queryFn: fetchGrantDashboard
  });

  if (isLoading) {
    return <LinearProgress />;
  }

  if (!dashboard) {
    return <Typography>No dashboard data available</Typography>;
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Transform data for charts
  const industryData = Object.entries(dashboard.categories.by_industry).map(([name, value]) => ({
    name,
    value
  }));

  const locationData = Object.entries(dashboard.categories.by_location).map(([name, value]) => ({
    name,
    value
  }));

  return (
    <Box sx={{ p: 3 }}>
      {/* Metrics Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" color="primary">Active Grants</Typography>
            <Typography variant="h3">{dashboard.metrics.total_active}</Typography>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" color="primary">Total Available</Typography>
            <Typography variant="h3">
              {formatCurrency(dashboard.metrics.total_amount_available)}
            </Typography>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" color="primary">Upcoming Deadlines</Typography>
            <Typography variant="h3">{dashboard.metrics.upcoming_deadlines}</Typography>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" color="primary">Avg Match Score</Typography>
            <Typography variant="h3">{Math.round(dashboard.metrics.avg_match_score)}%</Typography>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2, height: '400px' }}>
            <Typography variant="h6" gutterBottom>Grants by Industry</Typography>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart data={industryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#0088FE" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2, height: '400px' }}>
            <Typography variant="h6" gutterBottom>Grants by Location</Typography>
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie
                  data={locationData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {locationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Grid>
      </Grid>

      {/* Timeline */}
      <Card sx={{ p: 2, mb: 4 }}>
        <Typography variant="h6" gutterBottom>Grant Timeline</Typography>
        <Grid container spacing={2}>
          {Object.entries(dashboard.timeline).map(([period, data]) => (
            <Grid item xs={12} sm={6} md={2.4} key={period}>
              <Box sx={{ p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                <Typography variant="subtitle1" sx={{ textTransform: 'capitalize' }}>
                  {period.replace('_', ' ')}
                </Typography>
                <Typography variant="h6">{formatCurrency(data.total_amount)}</Typography>
                <Typography color="text.secondary">{data.count} grants</Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Card>

      {/* Insights */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Best Matches</Typography>
            {dashboard.matching_insights.best_matches.map((match, index) => (
              <Box key={match.grant_id} sx={{ mb: 2 }}>
                <Typography variant="subtitle1">{match.title}</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={match.score}
                    sx={{ flexGrow: 1 }}
                  />
                  <Typography variant="body2">{match.score}%</Typography>
                </Box>
              </Box>
            ))}
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Insights & Recommendations</Typography>
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" color="error" gutterBottom>
                Common Mismatches
              </Typography>
              {dashboard.matching_insights.common_mismatches.map((mismatch, index) => (
                <Chip
                  key={index}
                  label={mismatch}
                  color="error"
                  variant="outlined"
                  sx={{ m: 0.5 }}
                />
              ))}
            </Box>
            <Box>
              <Typography variant="subtitle2" color="primary" gutterBottom>
                Suggestions
              </Typography>
              {dashboard.matching_insights.suggested_improvements.map((suggestion, index) => (
                <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                  • {suggestion}
                </Typography>
              ))}
            </Box>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default GrantDashboard; 
import React from 'react';
import { Card, Grid, Typography, Box, Chip, LinearProgress } from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { grantsApi } from '@/services/grants';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const GrantDashboard: React.FC = () => {
  const { data: dashboard, isLoading, error } = useQuery({
    queryKey: ['grants', 'dashboard'],
    queryFn: grantsApi.getDashboard,
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });

  if (isLoading) {
    return <LinearProgress />;
  }

  if (error) {
    return (
      <Typography color="error">
        Error loading dashboard: {error instanceof Error ? error.message : 'Unknown error'}
      </Typography>
    );
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
    name: name.replace(/_/g, ' ').toUpperCase(),
    value
  }));

  const locationData = Object.entries(dashboard.categories.by_location).map(([name, value]) => ({
    name,
    value
  }));

  const fundingRangeData = Object.entries(dashboard.categories.by_funding_range).map(([name, value]) => ({
    name,
    value
  }));

  const orgTypeData = Object.entries(dashboard.categories.by_org_type).map(([name, value]) => ({
    name: name.replace(/_/g, ' ').toUpperCase(),
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

      {/* Additional Charts Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2, height: '400px' }}>
            <Typography variant="h6" gutterBottom>Grants by Funding Range</Typography>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart data={fundingRangeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#00C49F" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2, height: '400px' }}>
            <Typography variant="h6" gutterBottom>Grants by Organization Type</Typography>
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie
                  data={orgTypeData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {orgTypeData.map((entry, index) => (
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
              <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="subtitle2" color="text.secondary">
                  {period.replace(/_/g, ' ').toUpperCase()}
                </Typography>
                <Typography variant="h4" color="primary">
                  {data.count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {formatCurrency(data.total_amount)}
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Card>

      {/* Insights */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Best Matches</Typography>
            {dashboard.matching_insights.best_matches.map((match, index) => (
              <Box key={match.grant_id} sx={{ mb: 1, display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">{match.title}</Typography>
                <Chip 
                  label={`${match.score}%`} 
                  color={match.score >= 90 ? 'success' : match.score >= 75 ? 'warning' : 'default'}
                  size="small"
                />
              </Box>
            ))}
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Suggested Improvements</Typography>
            {dashboard.matching_insights.suggested_improvements.map((suggestion, index) => (
              <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                • {suggestion}
              </Typography>
            ))}
            
            {dashboard.matching_insights.common_mismatches.length > 0 && (
              <>
                <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>Common Issues</Typography>
                {dashboard.matching_insights.common_mismatches.map((mismatch, index) => (
                  <Typography key={index} variant="body2" color="error" sx={{ mb: 1 }}>
                    • {mismatch}
                  </Typography>
                ))}
              </>
            )}
          </Card>
        </Grid>
      </Grid>

      {/* Last Updated */}
      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          Last updated: {new Date(dashboard.last_updated).toLocaleString()}
        </Typography>
      </Box>
    </Box>
  );
};

export default GrantDashboard; 
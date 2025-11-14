import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class ReportGenerator:
    """Generate comprehensive financial reports and analytics"""
    
    def __init__(self):
        self.report_templates = self._load_report_templates()
    
    def _load_report_templates(self) -> Dict[str, Any]:
        """Load report templates"""
        return {
            'executive_summary': {
                'sections': ['overview', 'key_metrics', 'trends', 'recommendations']
            },
            'detailed_analysis': {
                'sections': ['transaction_analysis', 'category_breakdown', 'period_comparison', 'anomalies']
            },
            'accounting_report': {
                'sections': ['journal_summary', 'ledger_analysis', 'trial_balance', 'compliance']
            }
        }
    
    def generate_executive_summary(self, transactions_df: pd.DataFrame, 
                                 journal_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate executive summary report"""
        report = {
            'report_type': 'executive_summary',
            'generation_date': datetime.now().isoformat(),
            'sections': {}
        }
        
        # Overview section
        report['sections']['overview'] = self._generate_overview_section(transactions_df, journal_entries)
        
        # Key metrics section
        report['sections']['key_metrics'] = self._generate_key_metrics_section(transactions_df)
        
        # Trends section
        report['sections']['trends'] = self._generate_trends_section(transactions_df)
        
        # Recommendations section
        report['sections']['recommendations'] = self._generate_recommendations_section(transactions_df)
        
        return report
    
    def generate_detailed_analysis(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate detailed financial analysis report"""
        report = {
            'report_type': 'detailed_analysis',
            'generation_date': datetime.now().isoformat(),
            'sections': {}
        }
        
        if transactions_df.empty:
            return report
        
        # Transaction analysis
        report['sections']['transaction_analysis'] = self._generate_transaction_analysis(transactions_df)
        
        # Category breakdown
        report['sections']['category_breakdown'] = self._generate_category_breakdown(transactions_df)
        
        # Period comparison (if date data available)
        report['sections']['period_comparison'] = self._generate_period_comparison(transactions_df)
        
        # Anomaly detection
        report['sections']['anomalies'] = self._detect_anomalies(transactions_df)
        
        return report
    
    def _generate_overview_section(self, transactions_df: pd.DataFrame, 
                                 journal_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overview section"""
        total_transactions = len(transactions_df)
        journal_count = len(journal_entries)
        
        if not transactions_df.empty:
            total_amount = transactions_df['amount'].sum()
            credit_total = transactions_df[transactions_df['type'] == 'CR']['amount'].sum()
            debit_total = transactions_df[transactions_df['type'] == 'DR']['amount'].sum()
        else:
            total_amount = credit_total = debit_total = 0
        
        return {
            'total_transactions': total_transactions,
            'journal_entries_generated': journal_count,
            'total_amount_processed': total_amount,
            'credit_amount': credit_total,
            'debit_amount': debit_total,
            'net_balance': credit_total - debit_total,
            'processing_efficiency': f"{(journal_count / total_transactions * 100) if total_transactions > 0 else 0:.1f}%"
        }
    
    def _generate_key_metrics_section(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate key metrics section"""
        if transactions_df.empty:
            return {}
        
        metrics = {}
        
        # Basic metrics
        metrics['transaction_count'] = len(transactions_df)
        metrics['average_transaction_value'] = transactions_df['amount'].mean()
        metrics['largest_transaction'] = transactions_df['amount'].max()
        metrics['smallest_transaction'] = transactions_df['amount'].min()
        
        # Type distribution
        credit_count = len(transactions_df[transactions_df['type'] == 'CR'])
        debit_count = len(transactions_df[transactions_df['type'] == 'DR'])
        metrics['credit_debit_ratio'] = f"{credit_count}:{debit_count}"
        
        # Category metrics (if available)
        if 'category' in transactions_df.columns:
            unique_categories = transactions_df['category'].nunique()
            most_common_category = transactions_df['category'].mode().iloc[0] if not transactions_df['category'].mode().empty else 'N/A'
            metrics['unique_categories'] = unique_categories
            metrics['most_common_category'] = most_common_category
        
        return metrics
    
    def _generate_trends_section(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate trends analysis section"""
        if transactions_df.empty or 'date' not in transactions_df.columns:
            return {'message': 'Insufficient data for trend analysis'}
        
        try:
            trends = {}
            
            # Convert dates for analysis
            df_with_dates = transactions_df.copy()
            df_with_dates['date'] = pd.to_datetime(df_with_dates['date'], errors='coerce')
            df_with_dates = df_with_dates.dropna(subset=['date'])
            
            if df_with_dates.empty:
                return {'message': 'No valid dates for trend analysis'}
            
            # Monthly trends
            df_with_dates['month'] = df_with_dates['date'].dt.to_period('M')
            monthly_totals = df_with_dates.groupby('month')['amount'].sum()
            
            trends['monthly_totals'] = {
                str(month): amount for month, amount in monthly_totals.items()
            }
            
            # Identify trends
            if len(monthly_totals) > 1:
                trend_direction = "increasing" if monthly_totals.iloc[-1] > monthly_totals.iloc[0] else "decreasing"
                trends['overall_trend'] = trend_direction
            
            return trends
            
        except Exception as e:
            return {'error': f"Trend analysis failed: {str(e)}"}
    
    def _generate_recommendations_section(self, transactions_df: pd.DataFrame) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if transactions_df.empty:
            return ["No data available for recommendations"]
        
        # Check for high-value transactions
        high_value_threshold = transactions_df['amount'].quantile(0.9)
        high_value_count = len(transactions_df[transactions_df['amount'] > high_value_threshold])
        
        if high_value_count > 0:
            recommendations.append(
                f"Review {high_value_count} high-value transactions above ₹{high_value_threshold:,.2f}"
            )
        
        # Check category distribution
        if 'category' in transactions_df.columns:
            category_counts = transactions_df['category'].value_counts()
            if len(category_counts) > 10:
                recommendations.append(
                    "Consider consolidating transaction categories for better analysis"
                )
        
        # Check for potential duplicates
        potential_duplicates = self._find_potential_duplicates(transactions_df)
        if potential_duplicates:
            recommendations.append(
                f"Review {len(potential_duplicates)} potentially duplicate transactions"
            )
        
        if not recommendations:
            recommendations.append("No specific recommendations based on current analysis")
        
        return recommendations
    
    def _generate_transaction_analysis(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate detailed transaction analysis"""
        analysis = {}
        
        if transactions_df.empty:
            return analysis
        
        # Amount distribution
        analysis['amount_statistics'] = {
            'mean': transactions_df['amount'].mean(),
            'median': transactions_df['amount'].median(),
            'std_dev': transactions_df['amount'].std(),
            'q1': transactions_df['amount'].quantile(0.25),
            'q3': transactions_df['amount'].quantile(0.75)
        }
        
        # Transaction type analysis
        type_analysis = transactions_df['type'].value_counts().to_dict()
        analysis['type_distribution'] = type_analysis
        
        # Temporal analysis (if dates available)
        if 'date' in transactions_df.columns:
            try:
                df_with_dates = transactions_df.copy()
                df_with_dates['date'] = pd.to_datetime(df_with_dates['date'], errors='coerce')
                df_with_dates = df_with_dates.dropna(subset=['date'])
                
                if not df_with_dates.empty:
                    analysis['date_range'] = {
                        'start': df_with_dates['date'].min().strftime('%Y-%m-%d'),
                        'end': df_with_dates['date'].max().strftime('%Y-%m-%d'),
                        'days_covered': (df_with_dates['date'].max() - df_with_dates['date'].min()).days
                    }
            except:
                pass
        
        return analysis
    
    def _generate_category_breakdown(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate category-wise breakdown"""
        breakdown = {}
        
        if transactions_df.empty or 'category' not in transactions_df.columns:
            return breakdown
        
        category_stats = transactions_df.groupby('category').agg({
            'amount': ['sum', 'count', 'mean', 'max'],
            'type': 'first'
        }).round(2)
        
        # Flatten column names
        category_stats.columns = ['_'.join(col).strip() for col in category_stats.columns.values]
        breakdown['category_statistics'] = category_stats.to_dict('index')
        
        # Top categories by amount
        top_categories = transactions_df.groupby('category')['amount'].sum().nlargest(5)
        breakdown['top_categories_by_amount'] = top_categories.to_dict()
        
        return breakdown
    
    def _generate_period_comparison(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate period comparison analysis"""
        comparison = {}
        
        if transactions_df.empty or 'date' not in transactions_df.columns:
            return comparison
        
        try:
            df_with_dates = transactions_df.copy()
            df_with_dates['date'] = pd.to_datetime(df_with_dates['date'], errors='coerce')
            df_with_dates = df_with_dates.dropna(subset=['date'])
            
            if df_with_dates.empty:
                return comparison
            
            # Compare first and second half of period
            sorted_dates = df_with_dates['date'].sort_values()
            mid_point = len(sorted_dates) // 2
            
            first_half = df_with_dates[df_with_dates['date'] <= sorted_dates.iloc[mid_point]]
            second_half = df_with_dates[df_with_dates['date'] > sorted_dates.iloc[mid_point]]
            
            if not first_half.empty and not second_half.empty:
                comparison['period_comparison'] = {
                    'first_half': {
                        'transaction_count': len(first_half),
                        'total_amount': first_half['amount'].sum(),
                        'average_transaction': first_half['amount'].mean()
                    },
                    'second_half': {
                        'transaction_count': len(second_half),
                        'total_amount': second_half['amount'].sum(),
                        'average_transaction': second_half['amount'].mean()
                    },
                    'change_percentage': {
                        'transaction_count': f"{((len(second_half) - len(first_half)) / len(first_half) * 100):.1f}%",
                        'total_amount': f"{((second_half['amount'].sum() - first_half['amount'].sum()) / first_half['amount'].sum() * 100):.1f}%"
                    }
                }
            
            return comparison
            
        except Exception as e:
            return {'error': f"Period comparison failed: {str(e)}"}
    
    def _detect_anomalies(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalous transactions"""
        anomalies = {}
        
        if transactions_df.empty:
            return anomalies
        
        # Detect outliers using IQR method
        Q1 = transactions_df['amount'].quantile(0.25)
        Q3 = transactions_df['amount'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = transactions_df[
            (transactions_df['amount'] < lower_bound) | 
            (transactions_df['amount'] > upper_bound)
        ]
        
        if not outliers.empty:
            anomalies['statistical_outliers'] = {
                'count': len(outliers),
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'outlier_transactions': outliers[['date', 'description', 'amount']].to_dict('records')
            }
        
        # Detect potential duplicates
        potential_duplicates = self._find_potential_duplicates(transactions_df)
        if potential_duplicates:
            anomalies['potential_duplicates'] = potential_duplicates
        
        return anomalies
    
    def _find_potential_duplicates(self, transactions_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find potentially duplicate transactions"""
        duplicates = []
        
        if transactions_df.empty:
            return duplicates
        
        # Group by amount and description similarity
        grouped = transactions_df.groupby('amount')
        
        for amount, group in grouped:
            if len(group) > 1:
                # Check for similar descriptions
                for i, row1 in group.iterrows():
                    for j, row2 in group.iterrows():
                        if i >= j:
                            continue
                        
                        # Simple similarity check (could be enhanced with fuzzy matching)
                        desc1 = str(row1['description']).lower()
                        desc2 = str(row2['description']).lower()
                        
                        # Check if descriptions are similar
                        words1 = set(desc1.split())
                        words2 = set(desc2.split())
                        similarity = len(words1.intersection(words2)) / max(len(words1), len(words2))
                        
                        if similarity > 0.6:  # 60% similarity threshold
                            duplicates.append({
                                'transaction1': row1.to_dict(),
                                'transaction2': row2.to_dict(),
                                'similarity_score': similarity
                            })
        
        return duplicates
    
    def export_report_to_json(self, report: Dict[str, Any], output_path: str) -> str:
        """Export report to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"Report exported to JSON: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error exporting report to JSON: {e}")
            raise
    
    def generate_report_text_summary(self, report: Dict[str, Any]) -> str:
        """Generate human-readable text summary from report"""
        lines = []
        
        lines.append("FINANCIAL REPORT SUMMARY")
        lines.append("=" * 50)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        
        for section_name, section_data in report.get('sections', {}).items():
            lines.append(section_name.upper().replace('_', ' '))
            lines.append("-" * 30)
            
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    if isinstance(value, (int, float)):
                        lines.append(f"  {key.replace('_', ' ').title()}: {value:,.2f}")
                    else:
                        lines.append(f"  {key.replace('_', ' ').title()}: {value}")
            elif isinstance(section_data, list):
                for item in section_data:
                    lines.append(f"  • {item}")
            else:
                lines.append(f"  {section_data}")
            
            lines.append("")
        
        return "\n".join(lines)
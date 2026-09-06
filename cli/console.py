"""Rich console UI for Kisan Dost."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.columns import Columns
from rich.align import Align
from config import settings, URDU_PROMPTS, CROP_URDU_NAMES, PEST_URDU_NAMES
from models import FarmerProfile, FarmContext
import logging

logger = logging.getLogger(__name__)

import sys
console = Console(width=settings.console_width, force_terminal=True, legacy_windows=False)

class KisanDostConsole:
    """Rich console interface for Kisan Dost."""
    
    def __init__(self, language: str = "en"):
        self.language = language
        self.urdu_mode = language in ("ur", "roman_ur")
        self.console = console
    
    def print_header(self):
        """Print the Kisan Dost header."""
        title = "🌾 Kisan Dost - Farmer's Friend 🌾"
        if self.urdu_mode:
            title = "🌾 کسان دوست - کسانوں کا دوست 🌾"
        
        header = Panel(
            Align.center(Text(title, style="bold green")),
            subtitle="Terminal Agronomy Agent | OpenAI Agents SDK",
            border_style="green"
        )
        console.print(header)
        console.print()
    
    def print_greeting(self, farmer_name: str = None):
        """Print greeting message."""
        if self.urdu_mode:
            greeting = URDU_PROMPTS.get("greeting_roman", URDU_PROMPTS["greeting"])
        else:
            greeting = f"Assalam-o-Alaikum! I'm Kisan Dost. How can I help your farm today?"
        
        if farmer_name:
            greeting = greeting.replace("today?", f"{farmer_name}?")
        
        console.print(Panel(greeting, border_style="blue"))
        console.print()
    
    def print_help(self):
        """Print help information."""
        help_text = """
## Available Commands

**Slash Commands:**
- `/help` - Show this help
- `/lang [en|ur|roman_ur]` - Change language
- `/profile` - Show farmer profile
- `/context` - Show farm context
- `/history` - Show conversation history
- `/reset` - Reset conversation
- `/quit` or `/exit` - Exit Kisan Dost

**Example Questions:**
- "What should I plant this Rabi season on 5 acres in Multan?"
- "My cotton leaves are curling with tiny white insects"
- "How much Urea and DAP for 10 acres of wheat?"
- "What's the wheat price in Faisalabad mandi?"
- "When should I irrigate my maize crop?"
- "What's my profit estimate for cotton this season?"
- "What government schemes am I eligible for?"

**Language Support:**
- English (default)
- Urdu (اردو)
- Roman Urdu (Urdu in English script)
        """
        console.print(Markdown(help_text))
    
    def print_farmer_profile(self, profile: FarmerProfile):
        """Print farmer profile."""
        table = Table(title="Farmer Profile", border_style="cyan")
        table.add_column("Field", style="bold")
        table.add_column("Value")
        
        table.add_row("Farmer ID", profile.farmer_id)
        table.add_row("Name", profile.name or "Not set")
        table.add_row("District", profile.district)
        table.add_row("Province", profile.province.value.title())
        table.add_row("Language", profile.preferred_language.value)
        table.add_row("Total Queries", str(profile.total_queries))
        
        console.print(table)
        console.print()
    
    def print_farm_context(self, context: FarmContext):
        """Print farm context."""
        table = Table(title="Farm Context", border_style="yellow")
        table.add_column("Field", style="bold")
        table.add_column("Value")
        
        table.add_row("Land Size", f"{context.land_size_acres} acres")
        table.add_row("Soil Type", context.soil_type.value)
        table.add_row("Season", context.season.value)
        table.add_row("Water Availability", context.water_availability.value)
        table.add_row("Current Crop", context.current_crop or "Not set")
        table.add_row("Crop Stage", context.crop_stage.value if context.crop_stage else "Not set")
        table.add_row("Last Irrigation", str(context.last_irrigation_date) if context.last_irrigation_date else "Not set")
        table.add_row("Fertilizer Applied", "Yes" if context.fertilizer_applied else "No")
        
        console.print(table)
        console.print()
    
    def print_crop_plan(self, plan):
        """Print crop recommendation plan."""
        if not plan.primary_recommendation:
            console.print("[red]No suitable crops found for your conditions.[/red]")
            return
        
        primary = plan.primary_recommendation
        
        # Primary recommendation panel
        primary_text = f"""
**Primary Recommendation: {primary.crop_name.title()}** ({primary.category.value})
- Expected Yield: {primary.expected_yield_kg_per_acre:,.0f} kg/acre
- Expected Price: PKR {primary.expected_price_pkr_per_40kg:,.0f}/40kg
- Water Need: {primary.water_requirement_mm:.0f} mm
- Growing Days: {primary.growing_days}
- NPK Requirement: {primary.fertilizer_npk_kg_per_acre[0]}-{primary.fertilizer_npk_kg_per_acre[1]}-{primary.fertilizer_npk_kg_per_acre[2]} kg/acre
- **Estimated Profit: PKR {primary.profit_per_acre_pkr:,.0f}/acre**
- Suitability: {primary.suitability_score:.0%}
"""
        
        if primary.risk_factors:
            primary_text += "\n⚠️ **Risks:**\n" + "\n".join(f"- {r}" for r in primary.risk_factors)
        
        console.print(Panel(Markdown(primary_text), title="🌱 Top Recommendation", border_style="green"))
        
        # Alternatives table
        if plan.alternative_crops:
            alt_table = Table(title="Alternative Crops", border_style="blue")
            alt_table.add_column("Crop")
            alt_table.add_column("Yield (kg/acre)")
            alt_table.add_column("Price (PKR/40kg)")
            alt_table.add_column("Profit (PKR/acre)")
            alt_table.add_column("Suitability")
            
            for alt in plan.alternative_crops:
                alt_table.add_row(
                    alt.crop_name.title(),
                    f"{alt.expected_yield_kg_per_acre:,.0f}",
                    f"{alt.expected_price_pkr_per_40kg:,.0f}",
                    f"{alt.profit_per_acre_pkr:,.0f}",
                    f"{alt.suitability_score:.0%}"
                )
            
            console.print(alt_table)
        
        console.print(f"\n[dim]Reasoning: {plan.reasoning}[/dim]")
        console.print()
    
    def print_fertilizer_plan(self, plan):
        """Print fertilizer plan."""
        table = Table(title=f"Fertilizer Plan for {plan.crop.title()} ({plan.acres} acres)", border_style="yellow")
        table.add_column("Fertilizer")
        table.add_column("Bags/Acre")
        table.add_column("Total Bags")
        table.add_column("Price/Bag")
        table.add_column("Total Cost")
        
        for bag in plan.fertilizer_bags:
            table.add_row(
                bag.fertilizer_type.value.upper(),
                f"{bag.bags_needed:.2f}",
                f"{bag.bags_needed * plan.acres:.2f}",
                f"PKR {bag.price_per_bag_pkr:,.0f}",
                f"PKR {bag.total_cost_pkr * plan.acres:,.0f}"
            )
        
        console.print(table)
        console.print(f"\n**Total Cost: PKR {plan.total_cost_pkr:,.0f}** ({plan.cost_per_acre_pkr:,.0f}/acre)")
        
        if plan.subsidy_eligible:
            console.print(f"[green]✓ Subsidy Eligible: {plan.subsidy_details}[/green]")
        
        # Application schedule
        if plan.application_schedule:
            sched_table = Table(title="Application Schedule", border_style="blue")
            sched_table.add_column("Stage")
            sched_table.add_column("Fertilizer")
            sched_table.add_column("Bags/Acre")
            sched_table.add_column("Timing")
            
            for s in plan.application_schedule:
                sched_table.add_row(
                    s.get("stage", ""),
                    s.get("fertilizer", ""),
                    str(s.get("bags_per_acre", "")),
                    s.get("timing", "")
                )
            console.print(sched_table)
        
        console.print()
    
    def print_pest_diagnosis(self, diagnosis):
        """Print pest diagnosis."""
        # Diagnosis panel
        diag_text = f"""
**Diagnosis: {diagnosis.pest_name}** ({diagnosis.pest_type.value})
- Scientific Name: {diagnosis.scientific_name or 'N/A'}
- Confidence: {diagnosis.confidence:.0%}
- Severity: {diagnosis.severity.value.upper()}
- Symptoms Matched: {', '.join(diagnosis.symptoms_matched)}
- Affected Crops: {', '.join(diagnosis.affected_crops)}
"""
        
        if diagnosis.urdu_name:
            diag_text += f"\n- Urdu Name: {diagnosis.urdu_name}"
        
        if diagnosis.economic_threshold:
            diag_text += f"\n- Economic Threshold: {diagnosis.economic_threshold}"
        
        console.print(Panel(Markdown(diag_text), title="🔬 Diagnosis", border_style="red"))
        
        # Treatment
        treatment = diagnosis.treatment
        treat_text = f"""
**Treatment: {treatment.treatment_type.value.title()}**
- Pesticide: {treatment.pesticide_name or 'N/A'}
- Active Ingredient: {treatment.active_ingredient or 'N/A'}
- Dosage: {treatment.dosage_ml_per_acre:.0f} ml/acre
- Method: {treatment.application_method}
- Timing: {treatment.timing}
- Frequency: {treatment.frequency}
- Cost: PKR {treatment.cost_per_acre_pkr:,.0f}/acre
"""
        
        # Safety
        safety = treatment.safety
        treat_text += f"""
**Safety:**
- Max Safe Dosage: {safety.max_dosage_ml_per_acre:.0f} ml/acre
- Pre-Harvest Interval: {safety.pre_harvest_interval_days} days
- Re-Entry Interval: {safety.re_entry_interval_hours} hours
- PPE Required: {', '.join(safety.protective_equipment)}
- Bee Toxicity: {safety.bee_toxicity}
- Aquatic Toxicity: {safety.aquatic_toxicity}
"""
        
        console.print(Panel(Markdown(treat_text), title="💊 Treatment Plan", border_style="yellow"))
        
        # Alternatives
        if treatment.alternatives:
            alt_table = Table(title="Alternative Treatments", border_style="blue")
            alt_table.add_column("Type")
            alt_table.add_column("Name")
            alt_table.add_column("Dosage")
            alt_table.add_column("Cost")
            
            for alt in treatment.alternatives:
                alt_table.add_row(
                    alt.treatment_type.value,
                    alt.pesticide_name or alt.active_ingredient or "Cultural",
                    f"{alt.dosage_ml_per_acre:.0f} ml/acre" if alt.dosage_ml_per_acre > 0 else "N/A",
                    f"PKR {alt.cost_per_acre_pkr:,.0f}/acre"
                )
            console.print(alt_table)
        
        # Prevention
        if diagnosis.preventive_measures:
            prev_text = "\n".join(f"- {m}" for m in diagnosis.preventive_measures)
            console.print(Panel(Markdown(prev_text), title="🛡️ Prevention", border_style="green"))
        
        console.print()
    
    def print_mandi_prices(self, data: dict):
        """Print mandi prices."""
        table = Table(title=f"Mandi Prices for {data['commodity'].title()} in {data['district'].title()}", border_style="cyan")
        table.add_column("Mandi")
        table.add_column("Min (PKR/40kg)")
        table.add_column("Max (PKR/40kg)")
        table.add_column("Modal (PKR/40kg)")
        table.add_column("Arrivals (T)")
        
        for p in data["prices"]:
            table.add_row(
                p["mandi_name"].replace("_", " ").title(),
                f"{p['min_price_pkr_per_40kg']:,.0f}",
                f"{p['max_price_pkr_per_40kg']:,.0f}",
                f"{p['modal_price_pkr_per_40kg']:,.0f}",
                f"{p['arrivals_tonnes']:,.0f}" if p.get("arrivals_tonnes") else "N/A"
            )
        
        console.print(table)
        
        # Trends
        if data.get("trends"):
            trend_table = Table(title="Price Trends", border_style="blue")
            trend_table.add_column("Mandi")
            trend_table.add_column("7-Day Trend")
            trend_table.add_column("7-Day %")
            trend_table.add_column("30-Day Trend")
            trend_table.add_column("30-Day %")
            trend_table.add_column("Advice")
            
            for t in data["trends"]:
                trend_7d = t["trend_7d"]
                trend_30d = t["trend_30d"]
                
                trend_7d_style = "green" if trend_7d == "rising" else "red" if trend_7d == "falling" else "yellow"
                trend_30d_style = "green" if trend_30d == "rising" else "red" if trend_30d == "falling" else "yellow"
                
                trend_table.add_row(
                    t["mandi_name"].replace("_", " ").title(),
                    f"[{trend_7d_style}]{trend_7d}[/{trend_7d_style}]",
                    f"{t['change_percent_7d']:+.1f}%",
                    f"[{trend_30d_style}]{trend_30d}[/{trend_30d_style}]",
                    f"{t['change_percent_30d']:+.1f}%",
                    t["best_sell_window"]
                )
            
            console.print(trend_table)
        
        console.print(f"\n💡 **Advice:** {data['best_sell_window']}")
        console.print(f"[dim]Source: {data['data_source']} | Updated: {data['last_updated']}[/dim]")
        console.print()
    
    def print_profit_estimate(self, estimate):
        """Print profit estimate."""
        # Summary panel
        rec_style = "green" if estimate.recommendation == "profitable" else "yellow" if estimate.recommendation == "marginal" else "red"
        
        summary = f"""
**Crop:** {estimate.crop.title()} ({estimate.acres} acres)
**Total Input Cost:** PKR {estimate.total_input_cost_pkr:,.0f} ({estimate.total_input_cost_pkr/estimate.acres:,.0f}/acre)
**Expected Yield:** {estimate.expected_yield_kg:,.0f} kg total ({estimate.expected_yield_kg/estimate.acres:,.0f} kg/acre)
**Expected Price:** PKR {estimate.expected_price_pkr_per_40kg:,.0f}/40kg
**Expected Revenue:** PKR {estimate.expected_revenue_pkr:,.0f}
**Net Profit:** PKR {estimate.net_profit_pkr:,.0f} (Margin: {estimate.profit_margin_percent:.1f}%)
**Break-Even Yield:** {estimate.break_even_yield_kg_per_acre:,.1f} kg/acre
**Break-Even Price:** PKR {estimate.break_even_price_pkr_per_40kg:,.0f}/40kg
**Recommendation:** [{rec_style}]{estimate.recommendation.upper()}[/{rec_style}]
"""
        
        console.print(Panel(Markdown(summary), title="💰 Profit Estimate", border_style="green"))
        
        # Cost breakdown
        cost_table = Table(title="Cost Breakdown (per acre)", border_style="blue")
        cost_table.add_column("Input")
        cost_table.add_column("Cost (PKR/acre)")
        cost_table.add_column("% of Total")
        
        total_per_acre = estimate.total_input_cost_pkr / estimate.acres
        for item, cost in estimate.input_costs.items():
            cost_table.add_row(
                item.title(),
                f"{cost:,.0f}",
                f"{cost/total_per_acre*100:.1f}%"
            )
        
        console.print(cost_table)
        
        # Sensitivity
        sens_table = Table(title="Sensitivity Analysis (Profit per acre)", border_style="yellow")
        sens_table.add_column("Scenario")
        sens_table.add_column("Profit (PKR/acre)")
        
        for scenario, profit in estimate.sensitivity_analysis.items():
            sens_table.add_row(scenario.replace("_", " ").title(), f"{profit:,.0f}")
        
        console.print(sens_table)
        
        # Risks
        if estimate.risk_factors:
            risk_text = "\n".join(f"⚠️ {r}" for r in estimate.risk_factors)
            console.print(Panel(Markdown(risk_text), title="⚠️ Risk Factors", border_style="red"))
        
        console.print()
    
    def print_weather_forecast(self, forecast):
        """Print weather forecast and irrigation advice."""
        # Current conditions
        current_text = f"""
**Current Conditions:** {forecast.current_temp_c:.1f}°C, {forecast.current_humidity}% humidity
**Location:** {forecast.district} ({forecast.latitude:.2f}, {forecast.longitude:.2f})
"""
        console.print(Panel(Markdown(current_text), title="🌤️ Weather", border_style="blue"))
        
        # Forecast table
        fc_table = Table(title=f"{len(forecast.forecast)}-Day Forecast", border_style="cyan")
        fc_table.add_column("Date")
        fc_table.add_column("Max/Min (°C)")
        fc_table.add_column("Humidity")
        fc_table.add_column("Rain (mm)")
        fc_table.add_column("Wind (km/h)")
        fc_table.add_column("Condition")
        
        for f in forecast.forecast[:7]:
            fc_table.add_row(
                f.date.strftime("%a %d %b"),
                f"{f.temp_max_c:.1f}/{f.temp_min_c:.1f}",
                f"{f.humidity_percent:.0f}%",
                f"{f.precipitation_mm:.1f}",
                f"{f.wind_speed_kmh:.0f}",
                f.condition.value.replace("_", " ").title()
            )
        
        console.print(fc_table)
        
        # Irrigation advice
        irr = forecast.irrigation_advice
        irr_style = "green" if irr.should_irrigate else "yellow"
        
        irr_text = f"""
**Irrigate:** [{irr_style}]{'YES' if irr.should_irrigate else 'NO'}[/{irr_style}]
**Reason:** {irr.reason}
**Method:** {irr.method}
**Urgency:** {irr.urgency.upper()}
**Crop Stage:** {irr.crop_stage_context}
"""
        
        if irr.recommended_date:
            irr_text += f"\n**Recommended Date:** {irr.recommended_date.strftime('%d %b %Y')}"
        
        if irr.water_amount_mm > 0:
            irr_text += f"\n**Water Amount:** {irr.water_amount_mm:.1f} mm"
        
        console.print(Panel(Markdown(irr_text), title="💧 Irrigation Advice", border_style="blue"))
        
        # Alerts
        if forecast.alerts:
            for alert in forecast.alerts:
                console.print(Panel(alert, border_style="red"))
        
        console.print()
    
    def print_govt_schemes(self, schemes: list):
        """Print government schemes."""
        if not schemes:
            console.print("[yellow]No matching government schemes found for your profile.[/yellow]")
            return
        
        for match in schemes[:5]:
            scheme = match.scheme
            
            scheme_text = f"""
**{scheme.name}** ({scheme.scheme_type.value.replace('_', ' ').title()})
**Department:** {scheme.department}
**Province:** {scheme.province.title()}
**Match Score:** {match.match_score:.0%}

**Benefits:**
{chr(10).join(f'- {b}' for b in scheme.benefits)}

**Eligibility:**
- Land: {scheme.eligibility.min_land_acres or 'Any'} - {scheme.eligibility.max_land_acres or 'Any'} acres
- Crops: {', '.join(scheme.eligibility.required_crops) if scheme.eligibility.required_crops else 'All crops'}
- Farmer Category: {', '.join(scheme.eligibility.farmer_categories) if scheme.eligibility.farmer_categories else 'All'}

**Documents Required:** {', '.join(scheme.eligibility.documents_required) if scheme.eligibility.documents_required else 'Check with office'}

**Application:** {scheme.application_method.title()}
"""
            
            if scheme.application_url:
                scheme_text += f"\n**Online:** {scheme.application_url}"
            
            if scheme.contact_info:
                scheme_text += f"\n**Helpline:** {scheme.contact_info}"
            
            if scheme.application_deadline:
                scheme_text += f"\n**Deadline:** {scheme.application_deadline}"
            
            if match.next_steps:
                scheme_text += "\n\n**Next Steps:**\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(match.next_steps))
            
            console.print(Panel(Markdown(scheme_text), border_style="green"))
        
        console.print()
    
    def print_error(self, message: str):
        """Print error message."""
        console.print(Panel(f"[red]Error:[/red] {message}", border_style="red"))
    
    def print_warning(self, message: str):
        """Print warning message."""
        console.print(Panel(f"[yellow]Warning:[/yellow] {message}", border_style="yellow"))
    
    def print_info(self, message: str):
        """Print info message."""
        console.print(Panel(f"[blue]Info:[/blue] {message}", border_style="blue"))
    
    def get_input(self, prompt: str = "Your question") -> str:
        """Get user input."""
        if self.urdu_mode:
            prompt_text = URDU_PROMPTS.get("ask_symptoms_roman", "آپ کا سوال: ")
        else:
            prompt_text = f"{prompt}: "
        
        return Prompt.ask(prompt_text)
    
    def confirm(self, message: str) -> bool:
        """Get confirmation."""
        return Confirm.ask(message)
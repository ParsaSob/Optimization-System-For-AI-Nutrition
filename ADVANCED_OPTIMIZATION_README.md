# Advanced RAG Optimization Methods

## Overview

The RAG Meal Optimizer now implements 5 advanced optimization methods that provide superior results compared to simple scaling approaches. Each method has unique strengths and is automatically selected based on performance.

## 🎯 The 5 Optimization Methods

### 1. Linear Optimization with PuLP

**Method**: `_linear_optimize_pulp()`

**Description**: Uses linear programming to find the mathematically optimal solution for meal optimization.

**How it works**:
- Creates a linear optimization problem with PuLP
- Variables: grams of each ingredient (x₁, x₂, ..., xₙ)
- Objective: Minimize total calories
- Constraints: Meet minimum protein, carbs, and fat requirements
- Solver: CBC (Coin-OR Branch and Cut) solver

**Mathematical Formulation**:
```
Minimize: Σ(cᵢ × xᵢ)  # Total calories
Subject to:
  Σ(pᵢ × xᵢ) ≥ P_target  # Protein constraint
  Σ(cbᵢ × xᵢ) ≥ C_target  # Carbs constraint  
  Σ(fᵢ × xᵢ) ≥ F_target   # Fat constraint
  0 ≤ xᵢ ≤ max_qtyᵢ       # Quantity bounds
```

**Strengths**:
- ✅ Guaranteed optimal solution
- ✅ Fast execution for linear problems
- ✅ Precise constraint satisfaction
- ✅ Mathematical rigor

**Best for**: Linear nutritional relationships, precise macro targeting

---

### 2. Genetic Algorithm with DEAP

**Method**: `_genetic_algorithm_optimize()`

**Description**: Evolutionary algorithm that mimics natural selection to find near-optimal solutions.

**How it works**:
- **Population**: 100 individuals, each representing ingredient quantities
- **Selection**: Tournament selection (3-way competition)
- **Crossover**: Blend crossover (α=0.5) for mating
- **Mutation**: Gaussian mutation (σ=50) for diversity
- **Generations**: 50 evolution cycles
- **Fitness**: Calories + penalty for constraint violations

**Algorithm Flow**:
```
Initialize population → Evaluate fitness → Select parents → 
Crossover → Mutate → Evaluate offspring → Replace population → Repeat
```

**Strengths**:
- ✅ Handles non-linear relationships
- ✅ Global search capability
- ✅ Robust to local optima
- ✅ Adaptable to complex constraints

**Best for**: Non-linear optimization, complex nutritional interactions

---

### 3. Differential Evolution with SciPy

**Method**: `_differential_evolution_optimize()`

**Description**: Population-based evolutionary algorithm specifically designed for continuous optimization.

**How it works**:
- **Population**: 15 individuals
- **Mutation**: Differential mutation (F=0.5)
- **Crossover**: Binomial crossover (CR=0.7)
- **Iterations**: 100 maximum iterations
- **Cost Function**: Calories + squared penalty for constraints

**Differential Mutation Formula**:
```
v = x₁ + F × (x₂ - x₃)
```
Where F is the differential weight and x₁, x₂, x₃ are random population members.

**Strengths**:
- ✅ Excellent for continuous variables
- ✅ Fast convergence
- ✅ Good balance of exploration/exploitation
- ✅ Robust parameter tuning

**Best for**: Continuous optimization, smooth objective functions

---

### 4. Hybrid Optimization (GA + DE)

**Method**: `_hybrid_optimize()`

**Description**: Combines the exploration power of GA with the refinement capability of DE.

**How it works**:
1. **Phase 1**: Run Genetic Algorithm to find good initial solution
2. **Phase 2**: Use GA result to initialize DE population
3. **Phase 3**: Run Differential Evolution for refinement
4. **Fallback**: If DE fails, return GA result

**Hybrid Strategy**:
```
GA (Exploration) → Best Solution → DE Initialization → DE (Refinement) → Final Result
```

**Strengths**:
- ✅ Best of both worlds
- ✅ GA provides good starting point
- ✅ DE refines the solution
- ✅ Robust fallback mechanism

**Best for**: Complex optimization problems requiring both exploration and precision

---

### 5. Optuna Optimization

**Method**: `_optuna_optimize()`

**Description**: Hyperparameter optimization framework adapted for direct meal optimization.

**How it works**:
- **Trials**: 100 optimization trials
- **Sampling**: Tree-structured Parzen Estimator (TPE)
- **Objective**: Minimize calories + penalty
- **Parameter Space**: Continuous bounds for each ingredient quantity
- **Pruning**: Automatic trial pruning for efficiency

**Optuna Features**:
- Adaptive sampling based on previous results
- Efficient search space exploration
- Built-in visualization capabilities
- Parallel optimization support

**Strengths**:
- ✅ Intelligent sampling strategy
- ✅ Excellent for high-dimensional problems
- ✅ Built-in optimization history
- ✅ Extensible framework

**Best for**: High-dimensional optimization, adaptive sampling

---

## 🔧 Installation Requirements

To use all optimization methods, install the required libraries:

```bash
pip install -r requirements_advanced.txt
```

Or install individually:

```bash
pip install pulp deap scipy optuna numpy
```

## 📊 Method Selection & Evaluation

### Automatic Method Selection

The system automatically runs all available methods and selects the best result based on:

1. **Constraint Satisfaction**: How well macro targets are met
2. **Calorie Efficiency**: Lower calories for same nutrition
3. **Solution Quality**: Realistic ingredient quantities
4. **Computation Time**: Faster methods preferred

### Scoring Algorithm

```python
def calculate_optimization_score(actual, target):
    score = 0
    for macro in ['calories', 'protein', 'carbs', 'fat']:
        target_val = target[macro]
        actual_val = actual[macro]
        
        if target_val > 0:
            if actual_val > target_val:
                # Penalize over-target (5x penalty)
                diff = (actual_val - target_val) / target_val
                score += diff * diff * 5
            else:
                # Penalize under-target
                diff = (target_val - actual_val) / target_val
                score += diff * diff
    
    return score  # Lower is better
```

## 🚀 Performance Characteristics

| Method | Speed | Precision | Robustness | Best Use Case |
|--------|-------|-----------|------------|---------------|
| **PuLP** | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Linear problems, exact solutions |
| **DEAP GA** | ⚡⚡⚡ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Complex constraints, global search |
| **SciPy DE** | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Continuous optimization |
| **Hybrid** | ⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Best overall performance |
| **Optuna** | ⚡⚡⚡ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | High-dimensional problems |

## 🔍 Usage Examples

### Basic Usage

```python
from rag_optimization_engine_simple import RAGMealOptimizer

optimizer = RAGMealOptimizer()

result = optimizer.optimize_single_meal(
    rag_response=rag_response,
    target_macros=target_macros,
    user_preferences={},
    meal_type="lunch"
)

print(f"Best method: {result['optimization_result']['method']}")
print(f"Targets achieved: {result['target_achievement']['overall']}")
```

### Method-Specific Testing

```python
# Test individual methods
ingredients = [...]  # Your ingredient list
target_macros = {...}  # Your macro targets

# Test PuLP optimization
pulp_result = optimizer._linear_optimize_pulp(ingredients, target_macros)

# Test Genetic Algorithm
ga_result = optimizer._genetic_algorithm_optimize(ingredients, target_macros)

# Test Differential Evolution
de_result = optimizer._differential_evolution_optimize(ingredients, target_macros)
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_simple_rag.py
```

This will:
- Test all available optimization methods
- Show which libraries are available
- Demonstrate the complete optimization pipeline
- Provide installation guidance if needed

## 🔧 Troubleshooting

### Common Issues

1. **PuLP not available**: Install with `pip install pulp`
2. **DEAP import errors**: Install with `pip install deap`
3. **SciPy missing**: Install with `pip install scipy`
4. **Optuna not found**: Install with `pip install optuna`

### Fallback Behavior

If any method fails, the system automatically:
- Logs the error
- Continues with other methods
- Falls back to simple optimization if needed
- Provides detailed error information

## 📈 Advanced Configuration

### Customizing Method Parameters

```python
# Adjust DEAP parameters
optimizer.toolbox.register("population", tools.initRepeat, list, 
                          optimizer.toolbox.individual, n=200)  # Larger population

# Modify SciPy DE parameters
result = differential_evolution(
    cost, bounds,
    popsize=30,        # Larger population
    mutation=0.7,      # Higher mutation rate
    recombination=0.8, # Higher crossover rate
    maxiter=200        # More iterations
)
```

### Adding New Optimization Methods

```python
def _custom_optimize(self, ingredients, target_macros):
    # Your custom optimization logic
    pass

# Add to _run_optimization_methods
if hasattr(self, '_custom_optimize'):
    try:
        result = self._custom_optimize(ingredients, target_macros)
        results.append(result)
    except Exception as e:
        logger.warning(f"Custom optimization failed: {e}")
```

## 🎯 Best Practices

1. **Library Installation**: Install all libraries for best performance
2. **Method Selection**: Let the system automatically choose the best method
3. **Error Handling**: Check for method availability before use
4. **Performance Tuning**: Adjust parameters based on your specific use case
5. **Monitoring**: Use logging to track which methods succeed/fail

## 🔮 Future Enhancements

- **Machine Learning Integration**: Learn optimal method selection
- **Parallel Execution**: Run methods simultaneously
- **Custom Constraints**: User-defined optimization rules
- **Performance Profiling**: Detailed timing and resource usage
- **Method Chaining**: Sequential application of multiple methods

---

The advanced optimization methods provide a robust, intelligent approach to meal optimization that automatically adapts to different problem types and constraints, ensuring the best possible results for your nutritional goals.

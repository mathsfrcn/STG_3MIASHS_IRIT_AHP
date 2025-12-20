using LinearAlgebra, Statistics, CSV, DataFrames

# Matrix normalization
function normalize_matrix(matrix)
    col_sums = sum(matrix, dims=1)
    normalized_matrix = matrix ./ col_sums
    return normalized_matrix
end

# Priority vector
function priority_vector(normalized_matrix)
    # Mean of each row
    row_means = mean(normalized_matrix, dims=2)
    return vec(row_means)
end

# Consistency ratio 
function consistency_ratio(matrix, priority_vector)
    n = size(matrix, 1)
    λ_max = mean(matrix * priority_vector ./ priority_vector)
    ci = (λ_max - n) / (n - 1)
    
    ri_values = Dict(1 => 0.0, 2 => 0.0, 3 => 0.58, 4 => 0.90, 5 => 1.12, 6 => 1.24, 7 => 1.32, 8 => 1.41, 9 => 1.45, 10 => 1.49)
    ri = ri_values[n]
    
    cr = ci / ri
    return cr
end

# Aggregation moyenne arithmetique
function aggregate_matrices_arithmetic(matrices)
    n = size(matrices[1], 1)
    aggregated_matrix = zeros(n, n)
    
    for matrix in matrices
        aggregated_matrix .= aggregated_matrix .+ matrix
    end
    
    aggregated_matrix = aggregated_matrix ./ length(matrices)
    
    return aggregated_matrix
end

# AHP
function ahp_with_multiple_criteria(criteria_matrix, decision_matrices, alternatives)
    # 1. Normalize
    normalized_criteria_matrix = normalize_matrix(criteria_matrix)
    criteria_weights = priority_vector(normalized_criteria_matrix)
    
    println("Poids des critères : ", criteria_weights)
    
    # 2. Priority vector
    num_criteria = length(decision_matrices)
    num_alternatives = size(decision_matrices[1][1], 1)
    alternative_weights = zeros(num_alternatives, num_criteria)
    priority_vectors = []  
    normalized_matrices = []
    test = []
    consistency_ratios = []

    for i in 1:num_criteria
        # Aggregation of matrices
        aggregated_matrix = aggregate_matrices_arithmetic(decision_matrices[i])
        push!(test, aggregated_matrix)

        normalized_matrix = normalize_matrix(aggregated_matrix)
        
        push!(normalized_matrices, normalized_matrix)
        
        priority_vector_for_criterion = priority_vector(normalized_matrix)
        alternative_weights[:, i] = priority_vector_for_criterion
        
        push!(priority_vectors, priority_vector_for_criterion)

        cr = consistency_ratio(aggregated_matrix, priority_vector_for_criterion)
        println("Taux de cohérence pour le critère ", i, " : ", cr)
        if cr >= 0.1
            println("Attention : la cohérence pour le critère ", i, " est faible (CR > 0.1).")
        end

        # Calculate consistency ratio for each decision matrix
        cr_deciders = []
        for j in 1:length(decision_matrices[i])
            decider_matrix = decision_matrices[i][j]
            normalized_decider_matrix = normalize_matrix(decider_matrix)
            priority_vector_decider = priority_vector(normalized_decider_matrix)
            cr_decider = consistency_ratio(decider_matrix, priority_vector_decider)
            push!(cr_deciders, cr_decider)
        end
        push!(consistency_ratios, cr_deciders)
    end
    
    # 3. 
    final_weights = alternative_weights * criteria_weights
    
    alternative_ranking = [(alternatives[i], final_weights[i]) for i in 1:num_alternatives]
    
    # Ranking of alternatives
    sorted_ranking = sort(alternative_ranking, by=x->x[2], rev=true)
    
    # Display of final ranking
    println("\nClassement final des alternatives :")
    for (alternative, weight) in sorted_ranking
        println("Alternative : $alternative, Poids : $weight")
    end
    
    # Display of each matrices
    println("\nMatrices pour chaque critère :")
    for i in 1:num_criteria
        println("Matrice  pour le critère ", i, ":")
        println(test[i])
    end

    # Display of normalized matrices
    println("\nMatrices normalisées pour chaque critère :")
    for i in 1:num_criteria
        println("Matrice normalisée pour le critère ", i, ":")
        println(normalized_matrices[i])
    end
    
    # Display of priority vector
    println("\nVecteurs de priorités pour chaque critère :")
    for i in 1:num_criteria
        println("Critère ", i, ": ", priority_vectors[i])
    end

    # Display of consistency ratios for each decider
    println("\nTaux de cohérence pour chaque décideur et chaque critère :")
    for i in 1:num_criteria
        println("Critère ", i, ":")
        for j in 1:length(consistency_ratios[i])
            println("Décideur ", j, ": ", consistency_ratios[i][j])
        end
    end
    
    return sorted_ranking, priority_vectors, normalized_matrices, consistency_ratios
end

# Saisie de la matrice de comparaison des critères (3 critères)
criteria_matrix_decider1 = [
    1       1/7     3;
    7       1       3;
    1/3     1/3     1
]

criteria_matrix_decider2 = [
    1   1/5  5;
    5   1  2;
    1/5   1/2  1
]

criteria_matrix_decider3 = [
    1   1/3  1/9;
    3   1  1/9;
    9   9  1
]

criteria_matrices = [criteria_matrix_decider1, criteria_matrix_decider2, criteria_matrix_decider3]
criteria_matrix = aggregate_matrices_arithmetic(criteria_matrices)

# Alternatives
alternatives = ["Alternative 1", "Alternative 2", "Alternative 3", "Alternative 4", "Alternative 5", "Alternative 6", "Alternative 7", "Alternative 8", "Alternative 9", "Alternative 10"]

# Saisie des matrices de préférences pour chaque critère (10 alternatives, 3 décideurs)
# Critère 1
decider1_crit1 = CSV.File(raw".\TEST1612\crit1dec1.csv", types=Float64, header=false) |> DataFrame |> Matrix
decider2_crit1 = CSV.File(raw".\TEST1612\crit1dec2.csv", types=Float64, header=false) |> DataFrame |> Matrix
decider3_crit1 = CSV.File(raw".\TEST1612\crit1dec3.csv", types=Float64, header=false) |> DataFrame |> Matrix

# Critère 2
decider1_crit2 = CSV.File(raw".\TEST1612\crit2dec1.csv", types=Float64, header=false) |> DataFrame |> Matrix
decider2_crit2 = CSV.File(raw".\TEST1612\crit2dec2.csv", types=Float64, header=false) |> DataFrame |> Matrix
decider3_crit2 = CSV.File(raw".\TEST1612\crit2dec3.csv", types=Float64, header=false) |> DataFrame |> Matrix

# Critère 3
decider1_crit3 = CSV.File(raw".\TEST1612\crit3dec1.csv", types=Float64, header=false) |> DataFrame |> Matrix
decider2_crit3 = CSV.File(raw".\TEST1612\crit3dec2.csv", types=Float64, header=false) |> DataFrame |> Matrix
decider3_crit3 = CSV.File(raw".\TEST1612\crit3dec3.csv", types=Float64, header=false) |> DataFrame |> Matrix

# Liste de matrices pour chaque critère
decision_matrices = [
    [decider1_crit1, decider2_crit1, decider3_crit1],
    [decider1_crit2, decider2_crit2, decider3_crit2],
    [decider1_crit3, decider2_crit3, decider3_crit3]
]

# Appel de la fonction AHP avec 3 critères, 2 alternatives et 3 décideurs
final_ranking, priority_vectors, normalized_matrices, consistency_ratios = ahp_with_multiple_criteria(criteria_matrix, decision_matrices, alternatives)

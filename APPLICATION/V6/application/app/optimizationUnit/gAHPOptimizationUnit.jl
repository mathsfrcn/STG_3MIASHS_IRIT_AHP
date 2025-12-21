using LinearAlgebra, Statistics, CSV, DataFrames

# Matrix normalization
function normalize_matrix(matrix)
    #println("normalise_matrix type :", typeof(matrix))
    col_sums = sum(matrix, dims=1)
    normalized_matrix = matrix ./ col_sums
    return normalized_matrix
end

# Priority vector
function priority_vector(normalized_matrix)
    #println("priority_vecteur type :", typeof(normalized_matrix))
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

# Loading, aggregating, and verifying CSV criteria
function load_criteria_matrix(criteria_list_file, csv_output_criteria_path, decideur_list)
    # === 1. Check if the correct number of files was found ===
    ## Normally this condition is always valid because the check was carried out beforehand.
    expected_count = length(decideur_list)
    if length(criteria_list_file) == expected_count
        println("Tous les CSV criteres sont présents.")
        decision_criteria_global = Vector{Matrix{Float64}}()

        # === 2. Retrieving the contents of CSV files ===
        for filename in criteria_list_file
            file_path = joinpath(csv_output_criteria_path, filename)
            decision_criteria_local = CSV.File(file_path, header = false, types = Float64) |> DataFrame |> Matrix
            push!(decision_criteria_global, decision_criteria_local)
        end

        # === 3. If all files have been retrieved, aggregate the matrices. ===
        if length(decision_criteria_global) == length(criteria_list_file)
            criteria_matrix = aggregate_matrices_arithmetic(decision_criteria_global)
            return criteria_matrix
        else

            return nothing
        end
    else
        println("Erreur : $(length(criteria_list_file)) CSV criteres trouvés, mais $expected_count attendus.")
        return nothing
    end
end

# Loading and verifying alternative CSVs by criteria
function load_decision_matrix(csv_path, decideur_list, criteria_list, alternative_list_file)
    # Die dimensions
    nb_decideur = length(decideur_list)
    nb_criteria = length(criteria_list)

    # Number of files expected
    expected_count = nb_decideur * nb_criteria

    # === 1. Verification of the expected number of files ===
    if length(alternative_list_file) != expected_count
        println("Erreur : $(length(alternative_list_file)) CSV alternatives par critere trouvés, mais $expected_count attendus.")
        return nothing
    else
        println("Tous les CSV alternatives par critere sont présents.")
    end
    
    # === 2. Creation of the decision matrix ===
    decision_matrices = [Vector{Matrix{Float64}}(undef, nb_decideur) for _ in 1:nb_criteria]

    # === 3. CSV file processing ===
    for file in alternative_list_file
        filename = replace(basename(file), ".csv" => "")
        parts = split(filename, "_")    # Expected format : preference_alternative_NOMENTREPRISE_NOMDECIDEUR_NOMCRITERE_date.csv

        # === 3.1. Checking the CSV file name format ===
        if length(parts) != 8
            println("Impossible : nom du fichier $filename incorrect.")
            return nothing
        end

        # === 3.2. Retrieving the decision-maker's name and criteria ===
        dec = parts[4]
        crit = parts[5]
        
        if dec in decideur_list && crit in criteria_list
            # === 3.2.1. Retrieving the decision-maker's index and criteria from the appropriate lists ===
            i = findfirst(==(crit), criteria_list)
            j = findfirst(==(dec), decideur_list)

            # === 3.2.2. Retrieving the contents of the CSV file ===
            csv_matrix = CSV.File(csv_path * file, header = false, types = Float64) |> DataFrame |> Matrix

            # === 3.2.3. Matrix format check ===
            if size(csv_matrix, 1) != size(csv_matrix, 2)
                @warn "Erreur : la matrice contenue dans le fichier $filename n'est pas au bon format."
                return nothing
            # === 3.2.4. Adding the matrix to the main matrix ===
            else
                decision_matrices[i][j] = csv_matrix
            end
        else
            println("Décideur ou critère non reconnu dans le fichier : $filename.")
            return nothing
        end
    end
    return decision_matrices
end

# AHP
function ahp_with_multiple_criteria(csv_output_criteria_path, csv_alternative_path, decideur_list, criteria_list, alternative_list, criteria_list_file, alternative_list_file)
    # 0. Load decision_matrix and criteria_matrix
    criteria_matrix = load_criteria_matrix(criteria_list_file, csv_output_criteria_path, decideur_list)

    decision_matrix = load_decision_matrix(csv_alternative_path, decideur_list, criteria_list, alternative_list_file)
    
    # If files are missing, the program will stop.
    if decision_matrix === nothing || criteria_matrix === nothing
        return nothing
    end
    
    # 1. Normalize
    normalized_criteria_matrix = normalize_matrix(criteria_matrix)
    criteria_weights = priority_vector(normalized_criteria_matrix)
    
    println("Poids des critères : ", criteria_weights)
    
    # 2. Priority vector
    num_criteria = length(decision_matrix)
    num_alternatives = size(decision_matrix[1][1], 1)
    alternative_weights = zeros(num_alternatives, num_criteria)
    priority_vectors = []  
    normalized_matrices = []
    test = []
    consistency_ratios = []

    for i in 1:num_criteria
        # Aggregation of matrices
        aggregated_matrix = aggregate_matrices_arithmetic(decision_matrix[i])
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
        for j in 1:length(decision_matrix[i])
            decider_matrix = decision_matrix[i][j]

            normalized_decider_matrix = normalize_matrix(decider_matrix)
            priority_vector_decider = priority_vector(normalized_decider_matrix)
            cr_decider = consistency_ratio(decider_matrix, priority_vector_decider)
            push!(cr_deciders, cr_decider)
        end
        push!(consistency_ratios, cr_deciders)
    end
    
    # 3. 
    final_weights = alternative_weights * criteria_weights
    
    alternative_ranking = [(alternative_list[i], final_weights[i]) for i in 1:num_alternatives]
    
    # Ranking of alternatives
    sorted_ranking = sort(alternative_ranking, by=x->x[2], rev=true)
    
    # Display of final ranking
    #println("\nClassement final des alternatives :")
    #for (alternative, weight) in sorted_ranking
    #    println("Alternative : $alternative, Poids : $weight")
    #end
    
    # Display of each matrices
    #println("\nMatrices pour chaque critère :")
    #for i in 1:num_criteria
    #    println("Matrice  pour le critère ", i, ":")
    #    println(test[i])
    #end

    # Display of normalized matrices
    #println("\nMatrices normalisées pour chaque critère :")
    #for i in 1:num_criteria
    #    println("Matrice normalisée pour le critère ", i, ":")
    #    println(normalized_matrices[i])
    #end
    
    # Display of priority vector
    #println("\nVecteurs de priorités pour chaque critère :")
    #for i in 1:num_criteria
    #    println("Critère ", i, ": ", priority_vectors[i])
    #end

    # Display of consistency ratios for each decider
    #println("\nTaux de cohérence pour chaque décideur et chaque critère :")
    #for i in 1:num_criteria
    #    println("Critère ", i, ":")
    #    for j in 1:length(consistency_ratios[i])
    #        println("Décideur ", j, ": ", consistency_ratios[i][j])
    #    end
    #end
    
    return sorted_ranking
end
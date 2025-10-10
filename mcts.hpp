#include <iostream>
#include <cmath>
#include <vector>
#include <memory>
#include <unordered_map>
#include "include/chess.hpp"
#define exploitation_parameter 1.414
#define num_iterations 2000

class MCTSNode {
public:
    bool terminal;
    bool turn; // turn=true for WHITE, turn=false for BLACK
    unsigned int simulations;
    double score;
    bool chosen = false;

    int visits = 0;

    std::vector < std::shared_ptr<MCTSNode> > children;
    chess::Board state;
    chess::Move action;
    chess::Movelist untried_actions;

    MCTSNode *parent;

    MCTSNode(MCTSNode *parent, chess::Board state, chess::Move action)
        : parent(parent), state(state), action(action), score(0.0), simulations(0){
            /*
            children = new std::vector<MCTSNode*>();
            children->reserve(32);
            */
            actions_to_try(state);
            terminal = is_terminal(state);
            turn = state.sideToMove() == chess::Color::WHITE;
        }

    ~MCTSNode(){}

    void actions_to_try(chess::Board state){
        return chess::movegen::legalmoves(untried_actions, state);
    }

    bool is_terminal(chess::Board state){
        return state.isInsufficientMaterial() || state.isRepetition() || state.isHalfMoveDraw() || (state.getHalfMoveDrawType().first==chess::GameResultReason::CHECKMATE) || (state.getHalfMoveDrawType().first==chess::GameResultReason::STALEMATE);
    }

    int evaluate(chess::Board state) {
        if (state.isInsufficientMaterial() || state.isRepetition() || state.isHalfMoveDraw()
            || (state.getHalfMoveDrawType().first==chess::GameResultReason::STALEMATE)) {
            return 0;
        }
        else if(state.getHalfMoveDrawType().first==chess::GameResultReason::CHECKMATE) {
            if(state.sideToMove() == chess::Color::WHITE) return -1;
            else return 1;
        }
        return 0;
    }

    void flower() {
        while(!untried_actions.empty()) {
            expand();
        }
    }

    std::shared_ptr<MCTSNode> expand(){
        chess::Move move = untried_actions.back();
        chess::Movelist new_moves_list;

        for (auto m : untried_actions){
            if (m != move) new_moves_list.add(m);
        }

        untried_actions = new_moves_list;
        chess::Board new_state = state;
        new_state.makeMove(move);

        std::shared_ptr<MCTSNode> child = std::make_shared<MCTSNode> (this, new_state, move);

        children.push_back(child);

        return child;
    }

    double rollout() {
        chess::Board sim_state = state;

        while(!is_terminal(sim_state)) {
            chess::Movelist moves;
            chess::movegen::legalmoves(moves, sim_state);

            if(moves.empty()) break;

            srand(time(0));
            chess::Move random_move = moves[rand() % moves.size()];
            sim_state.makeMove(random_move);
        }

        score = evaluate(sim_state);

        return score;
    }

    bool is_fully_expanded() {
        return terminal || untried_actions.empty();
    }

    std::shared_ptr<MCTSNode> best_child(double c) {
        if (children.empty()) return nullptr;

        double ucb, m=-1;
        std::shared_ptr<MCTSNode> best = children.at(0);

        for (std::shared_ptr<MCTSNode> child : children){
            double q = child->score / ((double) child->simulations);
            ucb = c * sqrt(log(((double) this->simulations)) / ((double) child->simulations));

            if (turn) ucb += q;
            else ucb -= q;
            
            if (ucb > m){
                m = ucb;
                best = child;
            }
        }

        return best;
    } 

    void backpropagate(double result) {
        MCTSNode* node = this;

        while(node != nullptr) {
            node->simulations++;
            node->score += result;
            node = node->parent;
        }
    } 
};

class MCTSTree {
public:
    MCTSNode* root;

    MCTSTree(chess::Board state) {
        root = new MCTSNode(nullptr, state, chess::Move());
    }

    ~MCTSTree() {
        delete root;   
    }

    void run_search(MCTSNode* given_root, int iterations) {
        double average = 0;
        for(int i = 0; i < iterations; i++) {

            std::shared_ptr<MCTSNode> walker(given_root);

            // Selection
            while(!walker->terminal && walker->is_fully_expanded()) {
                walker = walker->best_child(exploitation_parameter);
            }
            
            // Expansion
            if(!walker->is_terminal(walker->state)) {
                walker = walker->expand();
            }

            // Rollout
            double result = walker->rollout();
            average += result;
            
        }
        given_root->score = average/iterations;
    }

};


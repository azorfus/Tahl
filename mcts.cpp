#include <iostream>
#include <unordered_map>
#include "chess.hpp"


class MCTSNode{
   public:
    bool terminal;
    chess::Board state;
    MCTSNode *parent;
    chess::Move action;
    std::vector<MCTSNode*> *children;
    unsigned int simulations;
    double score;
    chess::Movelist untried_actions;

    MCTSNode(MCTSNode *parent, chess::Board state, chess::Move action)
        : parent(parent), state(state), action(action), score(0.0), simulations(0){
            children = new std::vector<MCTSNode*>();
            children->reserve(32);
            actions_to_try(state);
            terminal = is_terminal(state);
        }

    ~MCTSNode(){
        for (auto* child : *children) delete child;
        delete children;
    }

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

    void expand(){
        chess::Move move = untried_actions.back();
        chess::Movelist new_moves_list;

        for (auto m : untried_actions){
            if (m != move) new_moves_list.add(m);
        }

        untried_actions = new_moves_list;
        chess::Board new_state = state;
        new_state.makeMove(move);
        MCTSNode* child = new MCTSNode(this, new_state, move);
        child->rollout();
        children->push_back(child);
    }

    void rollout() {
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
    }

    void backpropagate() {
        return;
    }
};
